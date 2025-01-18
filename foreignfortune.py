from utils import setup_driver, parse_html, save_to_json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

"""
Creating a list of URLs from which data needs to be extracted.

Returns:
    _type_: List of URLs containing product data to scrape.
"""

URLS = [
    "https://foreignfortune.com/collections/shoes",
    "https://foreignfortune.com/collections/foreign-accesories",
    "https://foreignfortune.com/collections/foreign-accesories?page=2"
]
BASE_URL = "https://foreignfortune.com"

def scrape_foreignfortune():
    """
    Main function to scrape product data from the Foreign Fortune website.

    This function navigates through the given URLs, extracts product details, 
    and saves the data in a JSON file. It handles page loading, extracts product 
    links, navigates to individual product pages, and collects details like title, 
    price, description, and images.

    Uses helper functions for setting up the web driver, parsing HTML, and saving 
    the extracted data.

    Raises:
        Exception: If the page fails to load or scraping encounters an error.
    """
    driver = setup_driver()  # Initialize the driver
    products = []  # To store all products

    for url in URLS:
        driver.get(url)
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="grid-view-item product-card"]'))
            )
        except Exception as e:
            print(f"Page not fully loaded for {url}, adding delay: {e}")
            pass
        
        selector = parse_html(driver.page_source)
        product_links = selector.xpath(
            '//div[@class="grid-view-item grid-view-item--sold-out product-card"]/a/@href | //div[@class="grid-view-item product-card"]/a/@href'
        ).getall()
        print(f"Found product links: {product_links}")

        for href in product_links:
            full_url = BASE_URL + href
            driver.get(full_url)  # Navigate to the product page
            response = parse_html(driver.page_source)
            product = scrape_from_product_page(full_url, response)
            if product:
                products.append(product)

    # Save all products to a JSON file
    save_to_json(products, "output/foreignfortune.json")
    print(f"Scraping complete. {len(products)} products saved to output/foreignfortune.json")
    driver.quit()  # Quit the driver after scraping

def scrape_from_product_page(full_url, response):
    """
    Scrape product details from an individual product page.

    Args:
        full_url (str): The full URL of the product page being scraped.
        response (Selector): Parsed HTML response of the product page.

    Returns:
        dict or None: Dictionary containing product details such as title, price, 
        description, images, and variants. Returns None if essential data is missing.
    
    Raises:
        Exception: If scraping encounters an error.
    """
    print("Inside product page")
    try:
        title = response.xpath('//h1/text()').get()
        price = response.xpath('//span[@id="ProductPrice-product-template"]/text()').get()
        image = response.xpath('//div[@class="product-single__photo-wrapper js"]/div/img/@src').get()
        images = response.xpath('//div[@class="product-single__photo-wrapper js"]/div/img/@src').getall()
        product_id = response.xpath('//div[@class="product-single__photo-wrapper js"]/div/img/@id').get()
        description = " ".join(response.xpath('//div[@class="product-single__description rte"]//text()').getall()).strip()
        variants = []

        # Extract variants (if available)
        for item in response.xpath('//li[@class = "grid__item medium-up--one-quarter product-single__thumbnails-item js"]'):
            variant_id = item.xpath('./a/@data-thumbnail-id').get()
            variant_image = item.xpath('./a/img/@src').get()
            size = item.xpath('./select/option/text()').get()
            variants.append({"id": variant_id if variant_id else ' ', "image": variant_image, "size": size if size else ' ', "price": price.strip() if price else ' '})

        # Return product data
        if title and price:
            return {
                "product_id": product_id or "N/A",
                "title": title.strip(),
                "image": image,
                "price": price.strip(),
                "description": description,
                "sale_prices": [price.strip()],
                "images": [images],
                "url": full_url,
                "brand": "Foreign Fortune Clothing",
                "models": {"color": "N/A", "variants": [variants]},
            }
        return None
    except Exception as e:
        print(f"Error scraping product at {full_url}: {e}")
        return None

if __name__ == "__main__":
    scrape_foreignfortune()
