"""
The purpose of this file is to provide immutable dicts that do not change for the purpose of this simulation. We fetch two dicts:

1) symbol_price_dict: contains dict of symbol : initial_value_CAD for desired coins
2) symbol_id_dict: contains dict of symbol : id for desired coins


This is to speed up processing time in the assets.py file where we make an API call to GeckoCoin API. This occurs because dict:

1) Provides a baseline set of values for initial_price_CAD. This is because there is a limited call rate on GeckoCoin API, this 
file provides more realistic data. In a production setting, this would be run asynchronously every few hours.

2) Instead of loading all assets in assets.py and then matching, we can fetch the necessary assets. These will not 
change as these are predefined in the requirements. This makes the size of our API call far smaller, executing the code faster.
To see how this was initially done, refer to old>inefficient_api.py, it was hecka slow.

"""

# Imports
import json
import os

import requests
from assets import ASSETS
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Function to fetch data from the API
def fetch_id_price():
    all_assets = []  # List to store assets
    page = 1
    # API
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "cad", "per_page": 250}
    headers = {
        "accept": "application/json",
        "x-cg-api-key": os.getenv("CoinGecko_API_Key"),
    }

    while True:
        params["page"] = page
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        all_assets.extend(data)

        # Stop fetching if less than 250 items are returned
        if len(data) < params["per_page"]:
            break
        page += 1

    return all_assets


data = fetch_id_price()

# Dictionaries to store values
symbol_price_dict = {}
symbol_id_dict = {}

for coin in data:
    if isinstance(coin, dict):
        symbol = coin.get("symbol", "").upper()
        if symbol in ASSETS:
            symbol_price_dict[symbol] = coin.get("current_price", "")
            symbol_id_dict[symbol] = coin.get("id", "")

# Paths to the Python files to be created
symbol_price_dict_file = os.path.join("backend", "src", "dicts", "symbol_price_dict.py")
symbol_id_dict_file = os.path.join("backend", "src", "dicts", "symbol_id_dict.py")

# Save symbol_price_dict as a Python file with cleaner formatting
with open(symbol_price_dict_file, "w") as f:
    f.write(f"symbol_price_dict = {json.dumps(symbol_price_dict, indent=4)}\n")

# Save symbol_id_dict as a Python file with cleaner formatting
with open(symbol_id_dict_file, "w") as f:
    f.write(f"SYMBOL_ID_DICT = {json.dumps(symbol_id_dict, indent=4)}\n")
