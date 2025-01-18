from utils import setup_driver, parse_html, save_to_json

URL = "https://www.lechocolat-alainducasse.com/uk/"
BASE_URL = "https://www.lechocolat-alainducasse.com"

def scrape_lechocolat():
    """
    Main function to scrape product data from the Le Chocolat Alain Ducasse website.

    This function navigates through the main category links, extracts product links,
    and collects product details such as title, price, description, and images from
    individual product pages. The data is saved into a JSON file.

    Uses helper functions for setting up the web driver, parsing HTML, and saving
    the extracted data.

    Raises:
        Exception: If page navigation or scraping encounters an error.
    """
    driver = setup_driver()  # Initialize the driver
    driver.get(URL)
    selector = parse_html(driver.page_source)
    links = selector.xpath('//li[@class="homeCategoryPads__item"]/a/@href').getall()
    products = []  # Creating a list to store all products

    """
    From the main listing page, extracting all the links of different product categories.
    """
    for link in links:
        driver.get(BASE_URL + link)
        selector = parse_html(driver.page_source)
        product_links = selector.xpath('//section[@class="productMiniature__data"]/a/@href').getall()
        print(f"Found product links: {product_links}")

        for href in product_links:
            driver.get(href)  # Navigate to the product page
            response = parse_html(driver.page_source)
            product = scrape_from_product_page(href, response)

            """Extracting product details from individual product pages."""
            if product:
                products.append(product)

    # Save all products to a JSON file
    save_to_json(products, "output/lechocolat.json")
    print(f"Scraping complete. {len(products)} products saved to output/lechocolat.json")
    driver.quit()  # Quit the driver after scraping

def scrape_from_product_page(href, response):
    """
    Scrape product details from an individual product page.

    Args:
        href (str): The full URL of the product page being scraped.
        response (Selector): Parsed HTML response of the product page.

    Returns:
        dict or None: Dictionary containing product details such as title, price,
        description, images, and product ID. Returns None if essential data is missing.

    Raises:
        Exception: If scraping encounters an error.
    """
    print("Inside product page")
    try:
        title = response.xpath('//h1/text()').get()
        price = response.xpath('//h3[contains(text(),"Price")]/following-sibling::p/text()').get()
        image = response.xpath('//li[@class="productImages__item keen-slider__slide"]/a/@href').get()
        images = response.xpath('//picture[@class="lazyloadBox product_cover"]/img/@srcset').getall()
        product_id = response.xpath('//div[@class="product-single__photo-wrapper js"]/div/img/@id').get()
        description = " ".join(response.xpath('//div[@class="productDescription"]/div/text()').getall()).strip()

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
                "url": href,
                "brand": "LE CHOCOLAT",
            }
        return None
    except Exception as e:
        print(f"Error scraping product at {href}: {e}")
        return None

if __name__ == "__main__":
    scrape_lechocolat()