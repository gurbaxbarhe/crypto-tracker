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
from dotenv import load_dotenv

from dicts.symbol_id_dict import symbol_id_dict

# Load environment variables from .env file
load_dotenv()

# API call
url = "https://api.coingecko.com/api/v3/coins/markets"
params = {"vs_currency": "cad", "ids": list([symbol_id_dict.values()])}
headers = {"accept": "application/json", "x-cg-api-key": os.getenv("CoinGecko_API_Key")}

response = requests.get(url, headers=headers, params=params)
data = response.json()

# Dictionaries to store values
symbol_price_dict = {}
symbol_id_dict = {}

for coin in data:
    symbol = coin["symbol"].upper()
    symbol_price_dict[symbol] = coin["current_price"]
    symbol_id_dict[symbol] = coin["id"]

# Paths to the Python files to be created
symbol_price_dict_file = os.path.join(
    ("backend", "src", "dicts"), "symbol_price_dict.py"
)
symbol_id_dict_file = os.path.join(("backend", "src", "dicts"), "symbol_id_dict.py")

# Save symbol_price_dict as a Python file with cleaner formatting
with open(symbol_price_dict_file, "w") as f:
    f.write(f"symbol_price_dict = {json.dumps(symbol_price_dict, indent=4)}\n")

# Save symbol_id_dict as a Python file with cleaner formatting
with open(symbol_id_dict_file, "w") as f:
    f.write(f"symbol_id_dict = {json.dumps(symbol_id_dict, indent=4)}\n")
