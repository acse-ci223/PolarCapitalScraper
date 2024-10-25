# This script scrapes investment fund data from Polar Capital's website and saves it to Excel
# It gets the top 10 positions for multiple funds and their corresponding weights

# Import necessary external tools (libraries)
import time  # For adding delays between actions
import pandas as pd  # For handling data in table format
from playwright.sync_api import sync_playwright  # For controlling a web browser
from bs4 import BeautifulSoup  # For reading website content
import re  # For finding specific text patterns

# Define the websites we want to get data from
# Main website where we'll handle cookies and terms of service
MAIN_URL = "https://www.polarcapital.co.uk/gb/individual/"

# List of specific fund pages we want to scrape data from
FUND_URLS = [
    "https://www.polarcapital.co.uk/gb/individual/Our-Funds/Artificial-Intelligence/#/Portfolio",
    "https://www.polarcapital.co.uk/gb/individual/Our-Funds/Emerging-Markets-Healthcare/#/Portfolio",
    "https://www.polarcapital.co.uk/gb/individual/Our-Funds/Financial-Opportunities/#/Portfolio"
]


def get_fund_name(url):
    """
    Takes a URL and extracts the fund name from it
    Example: Converts "Our-Funds/Artificial-Intelligence/#/Portfolio" to "Artificial Intelligence"
    """
    # Get the text between 'Our-Funds/' and '/#' in the URL
    fund_name = url.split('Our-Funds/')[1].split('/#')[0]
    # Convert hyphens to spaces for readability
    return fund_name.replace('-', ' ')


def accept_website_terms(page):
    """
    Handles the initial website popups:
    1. Accepts cookies
    2. Accepts terms of service
    This needs to be done before we can access the fund data
    """
    # Go to the main website
    page.goto(MAIN_URL)

    # Try to accept cookies (skip if it fails)
    try:
        page.evaluate("CookieInformation.submitAllCategories();")
    except Exception:
        pass

    # Try to accept terms of service (skip if it fails)
    try:
        page.wait_for_selector('a.Btn.-accept', timeout=10000)
        page.locator('a.Btn.-accept').click()
    except Exception:
        pass

    # Wait for everything to load
    time.sleep(1)


def extract_table_data(page):
    """
    Finds the top 10 positions table on the webpage and extracts:
    1. Position names
    2. Their weights in the portfolio
    Returns this data in a table format
    """
    # Get the entire webpage content
    html_content = page.content()

    # Parse the webpage content so we can search through it
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the section that contains "Top 10 Positions"
    header = soup.find(string=re.compile("Top 10 Positions", re.IGNORECASE))

    if header:
        # Find the table near this header
        table = header.parent.parent.find('table')
        if table:
            # Get all rows except the last one (which is usually a total)
            rows = table.find_all('tr')[:-1]

            # Create lists to store our data
            positions = []  # Will store position names
            weights = []    # Will store position weights

            # Go through each row and extract the data
            for row in rows:
                columns = row.find_all('td')
                if len(columns) >= 2:
                    positions.append(columns[0].get_text().strip())
                    weights.append(columns[1].get_text().strip())

            # Create a neat table (DataFrame) from our extracted data
            return pd.DataFrame({'Position': positions, 'Weight (%)': weights})

    # Return None if we couldn't find the table
    return None


def scrape_fund_data():
    """
    Main function that:
    1. Opens a web browser
    2. Goes to each fund page
    3. Extracts the data
    4. Returns all collected data
    """
    # List to store all our collected data
    fund_data = []

    # Start a web browser session
    with sync_playwright() as p:
        # Launch Chrome in background mode (no visible window)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("Accepting website terms...")
        # Handle the website terms first
        accept_website_terms(page)

        # Process each fund URL one by one
        for url in FUND_URLS:
            print(f"Processing fund: {url}")
            # Go to the fund's page
            page.goto(url)
            time.sleep(1)  # Wait for page to load

            # Try to get the fund's data
            current_fund_data = extract_table_data(page)
            if current_fund_data is not None:
                # Get fund name from the URL
                fund_name = get_fund_name(url) + " Fund"
                # Store both the data and fund name
                fund_data.append((current_fund_data, fund_name))

        # Close the browser when we're done
        browser.close()

    return fund_data


# This is where the script actually starts running
if __name__ == "__main__":
    # Get data from all funds
    fund_data = scrape_fund_data()

    # Save all the data to an Excel file
    # Each fund will be in its own sheet
    with pd.ExcelWriter('funds.xlsx') as excel_file:
        for data, sheet_name in fund_data:
            sheet_name = sheet_name[:31]
            data.to_excel(excel_file, sheet_name=sheet_name, index=False)