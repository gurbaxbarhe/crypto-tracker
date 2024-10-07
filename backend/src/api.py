"""
The purpose of this file is to handle the CoinGecko API fetch and simulate numbers for each coin based on baseline
values provided in dicts>symbol_price_dict.py. Also providing params for faster search via dicts>symbol_price_dict.py.

1) symbol_price_dict: contains dict of symbol : initial_value_CAD for desired coins
2) symbol_id_dict: contains dict of symbol : id for desired coins

This is to speed up processing time in the assets.py file where we make an API call to GeckoCoin API. This occurs because dict:
1) Provides a baseline set of values for initial_price_CAD. This is because there is a limited call rate on GeckoCoin API, this 
file provides more realistic data. In a production setting, this would be run asynchronously every few hours.

2) Instead of loading all assets in assets.py and then matching, we can fetch the necessary assets. These will not 
change as these are predefined in the requirements. This makes the size of our API call far smaller, executing the code faster.
To see how this was initially done, refer to old>inefficient_api.py, it was hecka slow.

WHY SEPERATE?
The separation is because this can be processed separately before startup while the web socket is initiating a new connection, and
it is easier to refetch data. Moreover, it's also cleaner to do so.
"""

# Imports
import os
import random
from datetime import datetime, timedelta

import requests
from dicts.assets import ASSETS
from dicts.symbol_id_dict import SYMBOL_ID_DICT
from dicts.symbol_price_dict import symbol_price_dict  # For symbol : initial_price_CAD
from dotenv import load_dotenv
from forex_python.converter import (  # For conversion to USD
    CurrencyRates,
    RatesNotAvailableError,
)

# Load environment variables from .env file
load_dotenv()

# Instantiate CurrencyRates object
usd_conversion = CurrencyRates()
try:
    conversion_rate = usd_conversion.get_rate("CAD", "USD")
except (RatesNotAvailableError, Exception) as e:
    conversion_rate = 1.3


# Function to fetch data from the API
def fetch_crypto_data(vs_currency="cad"):  # Default to CAD for currency
    all_assets = []  # List to store assets
    # URL for CoinGecko API
    url = "https://api.coingecko.com/api/v3/coins/markets"

    # Parameters for the API
    params = {
        "vs_currency": vs_currency,  # Default to CAD
        "per_page": 250,  # Fetch 250 results per page, as per CoinGecko documentation
        "ids": ",".join(
            SYMBOL_ID_DICT.values()
        ),  # Convert dict values to comma-separated string of coin IDs
        "page": 1,  # Begin at page 1
    }
    # Headers for the API key
    headers = {
        "accept": "application/json",
        "x-cg-api-key": os.getenv("CoinGecko_API_Key"),
    }
    page = 1

    while True:
        params["page"] = page
        data = []  # Initializing data as empty list
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            print(f"Failed due to: {e}")

        all_assets.extend(data)

        # Stop fetching if less than 250 items are returned
        if len(data) < params["per_page"]:
            break
        page += 1

    return all_assets


# Process and format asset data
def get_assets(vs_currency="cad"):
    data = fetch_crypto_data(vs_currency)  # Fetch new data

    # Change "symbol" to uppercase for matching
    for asset in data:
        if isinstance(asset, dict) and "symbol" in asset:
            asset["symbol"] = asset["symbol"].upper()

    def get_random_timestamp():
        random_date = datetime.now() - timedelta(days=random.randint(1, 30))
        return int(random_date.timestamp())

    def extract_keys(d):
        return {
            "name": d.get("name", "Unknown"),
            "symbol": d.get("symbol", "UNKNOWN"),
            "current_price": d.get("current_price", 0.0),
            "high_24h": d.get("high_24h", 0.0),
            "low_24h": d.get("low_24h", 0.0),
            "last_updated": d.get("last_updated", get_random_timestamp()),
            "price_change_24h": d.get("price_change_24h", 0.0),
            "price_change_percentage_24h": d.get("price_change_percentage_24h", 0.0),
        }

    # Filter assets based on provided symbols
    filtered_assets = [
        extract_keys(d)
        for d in data
        if isinstance(d, dict) and d.get("symbol", None) in ASSETS
    ]

    # Check for missing assets via symbols
    symbols_in_data = {
        d["symbol"] for d in data if isinstance(d, dict) and "symbol" in d
    }
    missing_assets = set(ASSETS) - symbols_in_data  # Finding the missing symbols

    """
    If there are missing assets, we get the spot_price based on the values from symbol_price_dict.py under backend>src>dicts
       
    The reason for this was because have an API call limit from the GeckoCoin API, limiting how many times we can run. 
    
    To simulate more real-world conditions the dict was made by running the GeckoCoin API once in dicts>fetch_id_initial_price.py.
    This file outputs a dict of the symbol:initial_price. This acts as our baseline values for the day.
        
    """
    if missing_assets:
        print(f"\n Missing assets from API call: {missing_assets} \n")
        for missing_asset in missing_assets:
            # Set previous week close to values that is stored in symbol_price_dict
            previous_week_close = symbol_price_dict.get(missing_asset)
            if previous_week_close is None:
                continue  # Skip that specific coin
            try:
                previous_week_close = float(previous_week_close)  # Must be float logic
            except ValueError:
                previous_week_close = random.randint(
                    0.1, 10
                )  # If it's still a pain, give random value for simulation

            if vs_currency == "usd":
                previous_week_close *= conversion_rate  # Conversion to USD

            # Get spot price from initial_prices_cad and ensure it ±50% of previous_week_close
            spot_price = round(previous_week_close * random.uniform(0.5, 1.5), 2)

            # Calculate bid and ask prices
            bid = round(
                spot_price * (1 - random.uniform(0.01, 0.05)), 2
            )  # Bid is slightly lower than spot
            ask = round(
                spot_price * (1 + random.uniform(0.01, 0.05)), 2
            )  # Ask is slightly higher than spot

            # Set yesterday's price to a random value between 90% and 110% of spot_price
            yesterday_price = round(
                random.uniform(0.90 * spot_price, 1.10 * spot_price), 2
            )

            # Calculate the percentage change over the last 24 hours
            price_change_percentage_24h = (
                round(((spot_price - yesterday_price) / yesterday_price * 100), 2)
                if yesterday_price != 0
                else random.uniform(
                    1, 50
                )  # Case where either spot_price or yesterday_price is zero
            )

            # Calculate the price change over the last 24 hours without abs
            price_change_24h = round(spot_price - yesterday_price, 2)

            # Generate a random timestamp within the past 30 days
            random_timestamp = get_random_timestamp()

            # Add missing asset to the list with values
            filtered_assets.append(
                {
                    "name": missing_asset,
                    "symbol": f"{missing_asset}",
                    "current_price": spot_price,
                    "high_24h": ask,
                    "low_24h": bid,
                    "last_updated": random_timestamp,
                    "price_change_24h": price_change_24h,
                    "price_change_percentage_24h": price_change_percentage_24h,
                }
            )

    # Continue processing
    # Convert "last_updated" from ISO 8601 format to Unix Epoch without decimals
    for unix_epoch in filtered_assets:
        if unix_epoch["last_updated"] and isinstance(unix_epoch["last_updated"], str):
            try:
                # Remove the trailing 'Z' if present and parse the timestamp
                unix_epoch["last_updated"] = int(
                    datetime.strptime(
                        unix_epoch["last_updated"].rstrip("Z"), "%Y-%m-%dT%H:%M:%S.%f"
                    ).timestamp()
                )
            except ValueError:
                # If parsing fails, assign the current timestamp
                unix_epoch["last_updated"] = int(datetime.now().timestamp())

        # Ensure numeric fields are not None
        for field in [
            "current_price",
            "high_24h",
            "low_24h",
            "price_change_24h",
            "price_change_percentage_24h",
        ]:
            if unix_epoch.get(field) is None:
                unix_epoch[field] = 0.0

    # Add _CAD suffix to each "symbol"
    suffix = "_CAD"
    for add_suffix in filtered_assets:
        add_suffix["symbol"] += suffix

    # Map old key names to new key names
    keys_renaming = {
        "last_updated": "timestamp",
        "low_24h": "bid",
        "high_24h": "ask",
        "current_price": "spot",
        "price_change_24h": "change",
        "price_change_percentage_24h": "change_percentage",
    }

    renamed_keys = []  # List to store renamed asset dictionaries

    for asset in filtered_assets:
        # 'name' and 'symbol' remain unchanged
        keys_renaming_dict = {
            "name": asset.get("name", "Unknown"),
            "symbol": asset.get("symbol", "UNKNOWN"),
        }
        # Rename other keys based on the mapping
        for old_key, new_key in keys_renaming.items():
            value = asset.get(old_key)
            if value is None:
                value = 0.0  # Assign default value if None
            keys_renaming_dict[new_key] = value

        renamed_keys.append(keys_renaming_dict)

    # Sort the assets by 'bid' descending
    sorted_renamed_keys = sorted(
        renamed_keys, key=lambda x: x.get("bid", 0.0), reverse=True
    )
    return sorted_renamed_keys


# Process formatting and data manipulation
get_assets_list = get_assets()
print(f"Asset information is: {get_assets_list}")
