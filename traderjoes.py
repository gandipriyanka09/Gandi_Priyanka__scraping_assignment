from utils import setup_driver, parse_html, save_to_json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time

URL = "https://www.traderjoes.com/home/products/category/food-8"
BASE_URL = "https://www.traderjoes.com"


def scrape_traderjoes():
    """
    Main function to scrape product data from Trader Joe's website.

    Navigates through product categories, extracts links to individual products,
    and collects product details such as title, price, description, and images.

    The collected data is saved into a JSON file.
    """
    products = []
    current_urls = [URL]  # List to store all pages

    # Use the driver context to ensure proper setup and teardown
    with setup_driver() as driver:
        driver.get(URL)

        while current_urls:
            current_url = current_urls[-1]
            print(f"Scraping page: {current_url}")

            try:
                # Extract product links for the current page
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, '//h2/a'))
                )
                link_elements = driver.find_elements(By.XPATH, '//h2/a')
                product_links = [link.get_attribute("href") for link in link_elements]

                for href in product_links:
                    full_url = href  # The full URL is already constructed
                    driver.get(full_url)
                    response = parse_html(driver.page_source)
                    product = scrape_from_product_page(full_url, response, driver)
                    if product:
                        products.append(product)
                        
                driver.get(current_urls[-1])

                # Try to locate and click the "Next" button (with added wait for visibility)
                try:
                    next_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, '//button[contains(@class, "Pagination_pagination__arrow__3TJf0 Pagination_pagination__arrow_side_right__9YUGr")]')
                        )
                    )
                    next_button.click()  # Click the button to go to the next page
                    print("Next button clicked successfully.")
                    time.sleep(2)
                    current_url = driver.current_url  # Wait for the next page to load
                    current_urls.append(current_url)

                except NoSuchElementException:
                    print("No 'Next' button found. Scraping completed.")
                    break
                except Exception as e:
                    print(f"Error during pagination: {e}")
                    break

            except Exception as e:
                print(f"Error during main scraping loop: {e}")
                break

        # Save the collected data to a JSON file
        save_to_json(products, "output/traderjoes.json")
        print(f"Scraping complete. {len(products)} products saved to output/traderjoes.json")


def scrape_from_product_page(full_url, response, driver):
    """
    Scrape product details from an individual product page.

    Args:
        full_url (str): URL of the product page.
        response (Selector): Parsed HTML response of the product page.

    Returns:
        dict or None: Dictionary containing product details like title, price,
        description, and images. Returns None if critical data is missing.
    """
    print(f"Scraping product details from: {full_url}")
    try:
        """I am scraping using Selenium because the content is not present in the page source.
        Even tried using headers, but the content was not yielded.
        """
        title = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//h1"))).text
        price = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//span[@class="ProductPrice_productPrice__price__3-50j"]'))).text
        image = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//img[@tabindex='-1']"))).get_attribute("src")
        images_att = driver.find_elements(By.XPATH, "//img[@tabindex='-1']")
        images = [img.get_attribute("src") for img in images_att]

        p_elements = driver.find_elements(By.XPATH, "//p")
        # Extract text from each <p> element
        description = [p.text for p in p_elements]

        # Return the product details as a dictionary
        return {
            "product_id": full_url.split('/')[-1],  # Extract product ID from URL
            "title": title.strip() if title else '',
            "image": image,
            "price": price.strip() if price else '',
            "description": " ".join(text for text in description),
            "url": full_url,
            "brand": "Trader Joe's",
            "images": images
        }
    except Exception as e:
        print(f"Error scraping product at {full_url}: {e}")
        return None


if __name__ == "__main__":
    scrape_traderjoes()
