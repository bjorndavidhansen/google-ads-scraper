import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
import random
import logging
import re
from fake_useragent import UserAgent
import os
from datetime import datetime

class GoogleAdsScraper:
    def __init__(self, headless=False):
        self.setup_logging()
        self.results = []
        self.setup_driver(headless)

    def setup_logging(self):
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = f'{log_dir}/scraping_{current_time}.log'

        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def setup_driver(self, headless=False):
        try:
            options = uc.ChromeOptions()

            if headless:
                options.add_argument('--headless')

            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-popup-blocking')

            # Random window size
            window_sizes = [(1920, 1080), (1366, 768), (1440, 900)]
            window_size = random.choice(window_sizes)
            options.add_argument(f'--window-size={window_size[0]},{window_size[1]}')

            # Random user agent
            ua = UserAgent()
            user_agent = ua.random
            options.add_argument(f'user-agent={user_agent}')

            self.driver = uc.Chrome(options=options)
            self.driver.set_page_load_timeout(30)

            logging.info("Driver setup successful")

        except Exception as e:
            logging.error(f"Driver setup failed: {str(e)}")
            raise

    def extract_ad_info(self, ad_element):
        try:
            link_element = ad_element.find_element(By.CSS_SELECTOR, 'a[data-rw]')
            title = link_element.text
            url = link_element.get_attribute('href')

            if url and '?' in url:
                url = url.split('?')[0]

            return title, url
        except Exception as e:
            logging.warning(f"Failed to extract ad info: {str(e)}")
            return None, None

    def extract_phone_number(self, text):
        patterns = [
            r'(?:\+61|0)?(?:4|\(04\))\s?\d{4}\s?\d{4}',  # Mobile
            r'(?:\+61|0)?(?:2|3|7|8)\s?\d{4}\s?\d{4}',   # Landline
            r'1[38]00\s?\d{3}\s?\d{3}',                  # 1300/1800
            r'13\s?\d{4}',                               # 13 numbers
            r'\b\d{8}\b',                                # Basic 8 digits
            r'\(\d{2}\)\s?\d{4}\s?\d{4}'                # (02) format
        ]

        phone_numbers = set()
        for pattern in patterns:
            matches = re.finditer(pattern, str(text))
            phone_numbers.update(match.group() for match in matches)

        return ', '.join(phone_numbers) if phone_numbers else None

    def get_website_content(self, url, max_retries=3):
        if not url:
            return None

        for attempt in range(max_retries):
            try:
                self.driver.execute_script("window.open('');")
                self.driver.switch_to.window(self.driver.window_handles[-1])

                time.sleep(random.uniform(1, 2))
                self.driver.get(url)

                scroll_pause = random.uniform(0.5, 1.0)
                total_height = int(self.driver.execute_script("return document.body.scrollHeight"))
                for scroll in range(0, total_height, random.randint(100, 300)):
                    self.driver.execute_script(f"window.scrollTo(0, {scroll});")
                    time.sleep(scroll_pause)

                page_source = self.driver.page_source

                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])

                return page_source

            except Exception as e:
                logging.error(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])

                if attempt == max_retries - 1:
                    return None

                time.sleep(random.uniform(3, 5))

    def search_google(self, keyword, location):
        try:
            search_query = f"{keyword} {location}"
            self.driver.get('https://www.google.com')

            try:
                consent_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label*="Consent"]'))
                )
                consent_button.click()
            except:
                pass

            time.sleep(random.uniform(1, 2))

            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, 'q'))
            )
            search_box.clear()

            for char in search_query:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))

            search_box.send_keys(Keys.RETURN)

            time.sleep(random.uniform(2, 3))

            ad_selectors = [
                'div[data-text-ad="1"]',
                'div[id^="tads"]',
                'div.commercial-unit-desktop-top'
            ]

            ads_found = False
            for selector in ad_selectors:
                try:
                    ads = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                    )
                    if ads:
                        ads_found = True
                        for ad in ads:
                            title, url = self.extract_ad_info(ad)

                            if url:
                                page_content = self.get_website_content(url)
                                if page_content:
                                    phone_number = self.extract_phone_number(page_content)

                                    self.results.append({
                                        'keyword': keyword,
                                        'location': location,
                                        'website_url': url,
                                        'phone_number': phone_number or "No phone found"
                                    })
                                    print(f"Found ad: {url}")
                                    logging.info(f"Successfully scraped ad for: {url}")
                except TimeoutException:
                    continue

            if not ads_found:
                logging.warning(f"No ads found for {search_query}")

            time.sleep(random.uniform(5, 8))

        except Exception as e:
            logging.error(f"Error in search_google for {search_query}: {str(e)}")
            self.handle_error()

    def handle_error(self):
        try:
            self.driver.quit()
        except:
            pass

        time.sleep(random.uniform(20, 30))
        self.setup_driver()

    def save_results(self, filename=None):
        if not filename:
            current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'google_ads_results_{current_time}.csv'

        try:
            if self.results:
                df = pd.DataFrame(self.results)
                df.to_csv(filename, index=False, encoding='utf-8-sig')
                logging.info(f"Results saved to {filename}")
                print(f"Successfully scraped {len(self.results)} ads")
            else:
                logging.warning("No results to save")
                print("No results found to save")
        except Exception as e:
            logging.error(f"Error saving results: {str(e)}")

    def close(self):
        try:
            self.driver.quit()
            logging.info("Driver closed successfully")
        except Exception as e:
            logging.error(f"Error closing driver: {str(e)}")

def main():
    keywords = ["window installation",
            "blinds" ]
    locations = ["Sydney","Brisbane","Melbourne"]

    print(f"Starting scraper with {len(keywords)} keywords and {len(locations)} locations")

    scraper = GoogleAdsScraper()

    try:
        total_combinations = len(keywords) * len(locations)
        current = 0

        for keyword in keywords:
            for location in locations:
                current += 1
                print(f"\nProgress: {current}/{total_combinations}")
                print(f"Processing: {keyword} - {location}")
                logging.info(f"Processing: {keyword} - {location}")
                scraper.search_google(keyword, location)
                time.sleep(random.uniform(8, 12))

        scraper.save_results()

    except KeyboardInterrupt:
        print("\nStopping scraper and saving results...")
        scraper.save_results()
    except Exception as e:
        logging.error(f"Main loop error: {str(e)}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
