# PolarCapitalScraper

# How it works

- An array with the requested links is defined at the top of [main](main.py)
- The links contain the tables that we will scrape.
- When first accessing the website, we get prompted to "Accept" cookies and agree with the ToS.
- A function handles that by calling the JavaScript code to close the cookies popup and then the ToS.
- Looping through the URLs, we find the HTML location of the "Top 10 Performing" title and get the table due to its relative position.
- Finally read each row of the HTML table and save it as a Pandas DataFrame.
- For post-processing, save all dataframes in a `.xlsx` file with each sheet being a fund.

# Installation
- Python 3.10 or above is required.

In order to run this script, we need to create an environment with the necessary packages.
```shell
virtualenv -p python3.10 .venv

source .venv/bin/activate

pip install -r requirements.txt

playwright install
```

# Running
After creating and activating the environment:
```python
python main.py
```

The program will scrape and create a `funds.xlsx` files with the scraped data.

