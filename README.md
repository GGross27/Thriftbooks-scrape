# ThriftBooks Web Scraper
## A Step-by-Step Guide for Junior Data Analysts

## Overview

This project is a beginner-friendly web scraping guide designed for junior data analytics interns at B&N Press. It walks through collecting book titles, prices, ratings, and URLs from ThriftBooks.com using Python, Selenium, and CSV/Pandas tools.

By the end of this guide, you will generate a structured CSV dataset containing thousands of book records that can be used for pricing analysis, market research, and trend discovery.

## Project Goals

- Teach web scraping fundamentals to junior data analysts
- Collect structured data from a real-world e-commerce website
- Output a clean CSV suitable for analysis and reporting
- Provide transferable automation and data collection skills

## Business Context

For publishing companies like B&N Press, understanding how books are priced and rated across popular retailers helps inform:

- Competitive pricing strategies
- Market trend analysis
- Marketing and promotion decisions
- Identification of underperforming or trending books

This project demonstrates how interns can autonomously gather actionable data, saving time and resources while supporting evidence-based decision-making.

## Target Audience

This guide assumes the reader is:

- A junior-level data analyst or CS student
- Familiar with Python basics (functions, loops, variables)
- Comfortable using VS Code and a terminal
- New or mostly new to web scraping

## ⚠️ Warnings & Cautions

### Library Versions
Using outdated versions of Python packages may cause crashes or unexpected behavior. Always install the latest versions listed below.

### Website-Specific Code
This scraper is tailored specifically to ThriftBooks.com. HTML structures, class names, and selectors will not transfer directly to other sites.

### Website Changes
Websites frequently update their HTML. If ThriftBooks changes its layout, this scraper may require maintenance.

## Technical Background

### Required Knowledge
- Python fundamentals
- Chrome browser usage
- Basic HTML structure and CSS selectors

### Required Python Packages
- Python 3.10+
- selenium
- webdriver-manager
- pandas or built-in csv

If your skill level or setup does not match the above, review Python basics and HTML fundamentals before proceeding.

## Required Materials

### Software
- VS Code
- Google Chrome (latest version)
- Excel or Google Sheets (for CSV review)

### Python Libraries
```bash
pip install selenium
pip install webdriver-manager
pip install pandas
```

## Project Structure
```
project-folder/
│
├── main.py
├── booktok_bestsellers.csv   # generated after execution
└── README.md
```

## Stage 1: Environment Setup

1. Create a new folder anywhere on your machine
2. Inside the folder, create a file named `main.py`
3. Open the folder in VS Code

### Starter Code (main.py)
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import csv

def main():
    pass

if __name__ == "__main__":
    main()
```

## Stage 2: Setting Up the Web Driver

Create a function to initialize the Selenium Chrome driver.
```python
def make_driver(headless=False):
    chrome_options = Options()
    chrome_options.add_argument('--remote-debugging-port=9222')

    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=chrome_options
    )
    return driver
```

In `main()`, initialize the driver and wrap execution in a try/finally block:
```python
driver = make_driver(headless=False)

try:
    url = "https://www.thriftbooks.com/browse/#b.s=bestsellers-desc&b.p=1&b.pp=50&b.f.t%5B%5D=15999"
    driver.get(url)
finally:
    driver.quit()
```

## Stage 3: Collect Book Links

### Purpose
Extract all individual book page URLs from the ThriftBooks bestseller pages.

### Key Concepts
- Use class names instead of long XPATHs when possible
- Handle pagination
- Avoid duplicate links

### Core Selector
```python
(By.CLASS_NAME, "SearchResultGridItem")
```

### Pagination Button Selector
```python
(By.CSS_SELECTOR, "button.Pagination-link.is-right.is-link")
```

This function navigates page-by-page until no next button exists, collecting unique book URLs.

## Stage 4: Scrape Book Details

For each collected book URL, extract:

- Title
- Rating
- Prices by format/condition

### Key Selectors

**Book Title**
```
.WorkMeta-title.Alternative.Alternative-title
```

**Price Buttons**
```
.NewButton.WorkSelector-button
```

### Output Format
Each book is stored as a dictionary containing:
- title
- rating
- url
- price fields (Hardcover, Paperback, etc.)

## Stage 5: Save Data to CSV
```python
def save_to_csv(data: list, filename="thriftbooks_data.csv"):
    if not data:
        print("No data to save.")
        return

    keys = data[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

    print(f"Saved {len(data)} rows to {filename}")
```

## Stage 6: Final main() Function
```python
def main():
    driver = make_driver(headless=False)

    try:
        url = "https://www.thriftbooks.com/browse/#b.s=bestsellers-desc&b.p=1&b.pp=50&b.f.t%5B%5D=15999"
        driver.get(url)

        book_links = get_book_links(driver)
        book_data = scrape_book_details(driver, book_links)
        save_to_csv(book_data, "booktok_bestsellers.csv")

    finally:
        driver.quit()
```

Run the program:
```bash
python main.py
```

⚠️ **Note:** Scraping thousands of books will take time. Leave the program running and ensure your device is plugged in.

## Optional: Small-Scale Testing

Limit scraping during development:
```python
book_links = get_book_links(driver, max_links=10)
book_data = scrape_book_details(driver, book_links, max_links=10)
```

## Final Deliverable

A CSV file containing 3,000+ books with columns including:
- Title
- URL
- Rating
- Prices by format/condition

Ready for analysis in Excel, Google Sheets, Pandas, or R.

## Key Takeaways

- Web scraping skills are highly transferable across data roles
- Simpler webpages often have cleaner HTML
- Selenium is powerful but requires maintenance
- Structured automation saves time, money, and effort
