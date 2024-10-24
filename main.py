import time
import pandas as pd
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# Function to scrape the table data from a given URL and table ID
def scrape_table_data(page, table_id):
    # Wait for the page to load
    time.sleep(1)

    # Get the page content after interaction
    html_content = page.content()

    # Parse the page content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the table with the specific ID
    table = soup.find('table', {'id': table_id})

    # Check if the table was found
    if table:
        # Extract data from the rows (excluding the footer row)
        rows = table.find_all('tr')[:-1]  # Skip the last row (footer with "Total")

        positions = []
        weights = []

        for row in rows:
            columns = row.find_all('td')
            position_name = columns[0].get_text().strip()
            weight = columns[1].get_text().strip()
            positions.append(position_name)
            weights.append(weight)

        # Create a dataframe from the scraped data
        df = pd.DataFrame({'Position': positions, 'Weight (%)': weights})
        return df
    else:
        print(f"Table with ID {table_id} not found.")
        return None

# Function to handle the entire scraping workflow for multiple URLs
def scrape_multiple_pages():
    # List of URLs and corresponding table IDs
    urls_and_tables = [
        ("https://www.polarcapital.co.uk/gb/individual/Our-Funds/Artificial-Intelligence/#/Portfolio", "c33074f2-acb5-4725-b2af-6570d30e11eb"),
        ("https://www.polarcapital.co.uk/gb/individual/Our-Funds/Emerging-Markets-Healthcare/#/Portfolio", "e12a3f1b-70c0-4e58-bf07-8637a0d0aa02"),
        ("https://www.polarcapital.co.uk/gb/individual/Our-Funds/Financial-Opportunities/#/Portfolio", "dbc69301-3cd8-4ea2-84d0-ecbc3d5358d5")
    ]

    with sync_playwright() as p:
        # Start a browser (headless mode can be False for debugging)
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        dataframes = []  # To store dataframes for all three tables

        # First URL: Handle cookies and ToS only once
        first_url, first_table_id = urls_and_tables[0]
        page.goto(first_url)

        # Accept cookies via JavaScript
        try:
            page.evaluate("CookieInformation.submitAllCategories();")
            print("Accepted cookies via JavaScript.")
        except Exception as e:
            print(f"Error while executing cookie acceptance JavaScript: {e}")

        # Accept Terms of Service (ToS)
        try:
            page.wait_for_selector('a.Btn.-accept', timeout=10000)  # Wait for the button to appear
            tos_button = page.locator('a.Btn.-accept')
            tos_button.click()
            print("Accepted Terms of Service.")
        except Exception as e:
            print(f"Error while accepting Terms of Service: {e}")

        # Scrape the table data for the first URL
        df1 = scrape_table_data(page, first_table_id)
        if df1 is not None:
            dataframes.append((df1, "Artificial Intelligence"))

        # Scrape data for the remaining URLs without accepting cookies/ToS again
        for url, table_id in urls_and_tables[1:]:
            page.goto(url)
            print(f"Navigating to {url}...")

            # Scrape the table data for subsequent URLs
            df = scrape_table_data(page, table_id)
            if df is not None:
                sheet_name = "Emerging Markets" if "Emerging" in url else "Financial Opportunities"
                dataframes.append((df, sheet_name))

        # Close the browser
        browser.close()

        return dataframes

# Call the function to scrape the pages and get the dataframes
dataframes = scrape_multiple_pages()

# Save the dataframes to an Excel file with each dataframe in a separate sheet
with pd.ExcelWriter('funds.xlsx') as writer:
    for df, sheet_name in dataframes:
        df.to_excel(writer, sheet_name=sheet_name, index=False)

print("Data successfully written to 'funds.xlsx'.")
