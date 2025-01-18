# utils.py
from parsel import Selector
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    """Set up a Selenium WebDriver."""
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def parse_html(html_content):
    """Parse HTML content using Parsel."""
    return Selector(text=html_content)

def save_to_json(data, output_file):
    """Save the data to a JSON file."""
    import json
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
