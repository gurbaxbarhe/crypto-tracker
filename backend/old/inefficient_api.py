import os
import random
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

from ..src.dicts.Excel.initial_prices import initial_prices_cad

# Load environment variables from .env file
load_dotenv()

# URL GeckoCoin URL
url = "https://api.coingecko.com/api/v3/coins/markets"

# Parameters for URL
params = {
    "vs_currency": "cad",  # Default to CAD, will switch to USD on frontend
    "per_page": 250,  # Fetch 250 results per page, as per Gecko documentation
    "page": 1,  # Begin at page 1
}

# Headers with API key
headers = {"accept": "application/json", "x-cg-api-key": os.getenv("CoinGecko_API_Key")}

# List of provided assets
ASSETS = [
    "BTC",
    "ETH",
    "LTC",
    "XRP",
    "BCH",
    "USDC",
    "XMR",
    "XLM",
    "USDT",
    "QCAD",
    "DOGE",
    "LINK",
    "MATIC",
    "UNI",
    "COMP",
    "AAVE",
    "DAI",
    "SUSHI",
    "SNX",
    "CRV",
    "DOT",
    "YFI",
    "MKR",
    "PAXG",
    "ADA",
    "BAT",
    "ENJ",
    "AXS",
    "DASH",
    "EOS",
    "BAL",
    "KNC",
    "ZRX",
    "SAND",
    "GRT",
    "QNT",
    "ETC",
    "ETHW",
    "1INCH",
    "CHZ",
    "CHR",
    "SUPER",
    "ELF",
    "OMG",
    "FTM",
    "MANA",
    "SOL",
    "ALGO",
    "LUNC",
    "USTC",
    "ZEC",
    "XTZ",
    "AMP",
    "REN",
    "UMA",
    "SHIB",
    "LRC",
    "ANKR",
    "HBAR",
    "EGLD",
    "AVAX",
    "ONE",
    "GALA",
    "ALICE",
    "ATOM",
    "DYDX",
    "CELO",
    "STORJ",
    "SKL",
    "CTSI",
    "BAND",
    "ENS",
    "RENDER",
    "MASK",
    "APE",
]


def fetch_crypto_data():
    all_assets = []  # List to store results of information from assets
    page = 1  # Begin at page 1

    while True:
        params["page"] = page
        # GET request from API
        response = requests.get(url, headers=headers, params=params)

        # Output data in JSON format
        data = response.json()

        # Adding each of the elements to the list
        all_assets.extend(data)

        # Check if results do not meet 250, then break
        if len(data) < params["per_page"]:
            break
        page += 1  # Check next page

    return all_assets


def get_assets(data):

    # Change "symbol" to uppercase for matching
    for asset in data:
        if isinstance(asset, dict) and "symbol" in asset:
            asset["symbol"] = asset["symbol"].upper()

    # Generate random timestamp for missing assets
    def get_random_timestamp():
        random_date = datetime.now() - timedelta(
            days=random.randint(1, 30)
        )  # Any random date for the past 30 days
        return int(random_date.timestamp())  # Convert to int to remove decimals

    # Extract the wanted keys as given in end point
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

    # Print the missing assets
    if missing_assets:
        print(f"\n Missing assets: {missing_assets} \n")
        for missing_asset in missing_assets:
            # Get spot price from initial_prices_cad
            spot_price = initial_prices_cad.get(missing_asset)
            spot_price = float(spot_price)  # SWpot_price is a float

            # Calculate bid and ask prices
            bid = round(
                spot_price * (1 - random.uniform(0.01, 0.05)), 2
            )  # Bid is slightly lower than spot
            ask = round(
                spot_price * (1 + random.uniform(0.01, 0.05)), 2
            )  # Ask is slightly higher than spot

            # Assigning previous_week_close as a value
            previous_week_close = round(spot_price * random.uniform(0.9, 0.99), 2)

            # Ensure yesterday's price is within ±50% of the previous week's close
            lower_bound = previous_week_close * 0.5
            upper_bound = previous_week_close * 1.5

            # Set random price for yester_day price
            yesterday_price = round(random.uniform(lower_bound, upper_bound), 2)

            # Calculate the percentage change over the last 24 hours
            if yesterday_price != 0:
                price_change_percentage_24h = round(
                    ((spot_price - yesterday_price) / yesterday_price) * 100, 2
                )
            else:
                price_change_percentage_24h = random.uniform(
                    1, 50
                )  # Case where yesterday_price is zero

            # Calculate the absolute price change over the last 24 hours
            price_change_24h = abs(round(spot_price - yesterday_price, 2))

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


# Fetch all data
fetch_all_crypto_data = fetch_crypto_data()

# Process formatting and data manipulation
get_assets_list = get_assets(fetch_all_crypto_data)
# print(f"Asset information is: {get_assets_list}")
