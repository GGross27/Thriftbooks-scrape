
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import csv

def make_driver(headless=False):
    chrome_options = Options()
    chrome_options.add_argument('--remote-debugging-port=9222')
    #chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

    return driver

def get_book_links(driver, max_links: int = None) -> list:
    """
    Scrapes book links from ThriftBooks BookTok bestseller pages.
    Navigates across pages until no more 'next' button is available
    or until max_links is reached (if provided).

    Parameters:
    - driver: Selenium WebDriver instance
    - max_links: optional int, limit number of links collected

    Returns:
    - list of book URLs
    """
    book_links = []

    try:
        while True:
            # wait until book links are visible
            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "SearchResultGridItem"))
            )
            sleep(2)  # let page settle

            # grab all book link elements
            link_elements = driver.find_elements(By.CLASS_NAME, "SearchResultGridItem")

            # extract hrefs and add to list
            for el in link_elements:
                href = el.get_attribute("href")
                if href and href not in book_links:
                    book_links.append(href)

                    # stop if we’ve reached max_links
                    if max_links is not None and len(book_links) >= max_links:
                        print(f"Reached max_links={max_links}. Stopping.")
                        return book_links

            print(f"Collected {len(link_elements)} links on this page. Total so far: {len(book_links)}")

            # check if next button is enabled
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.Pagination-link.is-right.is-link"))
                )
                is_disabled = (
                    next_button.get_attribute("disabled") is not None
                    or next_button.get_attribute("aria-disabled") == "true"
                )

                if is_disabled:
                    print("Reached last page.")
                    break
                else:
                    driver.execute_script("arguments[0].click();", next_button)
                    sleep(3)  # allow new page to load
            except Exception:
                print("No next button found, stopping.")
                break

    except Exception as e:
        print(f"Error scraping links: {e}")

    return book_links

def scrape_book_details(driver, links: list, max_links: int = None) -> list:
    """
    Scrape details from ThriftBooks book pages:
    - Title
    - Rating number
    - Price for each format/condition (Hardcover, Paperback, Library Binding, Like New, Very Good, Good, Acceptable, New)

    Parameters:
    - driver: Selenium WebDriver instance
    - links: list of book URLs
    - max_links: optional limit on number of links to scrape

    Returns a list of dictionaries (rows), ready for CSV export.
    """
    results = []

    # Limit the number of links if max_links is set
    if max_links is not None:
        links = links[:max_links]

    for i, link in enumerate(links, start=1):
        try:
            driver.get(link)
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".WorkMeta-title.Alternative.Alternative-title"))
            )
            sleep(2)

            # --- Title ---
            title_el = driver.find_element(By.CSS_SELECTOR, ".WorkMeta-title.Alternative.Alternative-title")
            title = title_el.text.strip()

            # --- Rating ---
            try:
                rating = driver.find_element(
                    By.CSS_SELECTOR, "meta[itemprop='ratingValue']"
                ).get_attribute("content")
            except:
                rating = "N/A"

            # --- Prices by format/condition ---
            formats = [
                "Hardcover", "Paperback", "Library Binding",
                "Like New", "Very Good", "Good", "Acceptable", "New"
            ]
            prices_dict = {fmt: "N/A" for fmt in formats}

            try:
                price_buttons = driver.find_elements(By.CSS_SELECTOR, ".NewButton.WorkSelector-button")
                for btn in price_buttons:
                    text = btn.text.strip()
                    for fmt in formats:
                        if text.startswith(fmt) or fmt in text:
                            # remove duplicate format mentions, keep only the price
                            clean_price = text.replace(fmt, "").strip()
                            prices_dict[fmt] = clean_price if clean_price else "N/A"
            except Exception:
                pass


            # --- Combine into row ---
            row = {
                "Title": title,
                "Rating": rating,
                "URL": link,
                **prices_dict
            }

            results.append(row)
            print(f"[{i}/{len(links)}] Scraped: {title}")

        except Exception as e:
            print(f"Failed on link {link}: {e}")

    return results


def save_to_csv(data: list, filename="thriftbooks_data.csv"):
    """ Save list of dicts into a CSV file. """
    if not data:
        print("No data to save.")
        return

    keys = data[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    print(f"Saved {len(data)} rows to {filename}")


def main():
    driver = make_driver(headless=False)
    
    try:
        url = "https://www.thriftbooks.com/browse/#b.s=bestsellers-desc&b.p=1&b.pp=50&b.f.t%5B%5D=15999"
        driver.get(url)
        
        # Step 1: collect all book links
        book_links = get_book_links(driver)
        print(book_links)
        
        # Step 2: scrape details
        book_data = scrape_book_details(driver, book_links)

        # Step 3: save to CSV
        save_to_csv(book_data, "booktok_bestsellers.csv")

    finally:
        driver.quit()
 
if __name__ == "__main__":
    main()