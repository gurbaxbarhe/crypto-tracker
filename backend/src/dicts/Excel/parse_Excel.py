import json

import pandas as pd

# Load the Excel file and convert it to a dictionary
df = pd.read_excel("extra/asset_prices.xlsx", header=None, skiprows=1)
output = dict(zip(df[0], df[1]))
initial_prices_cad = json.dumps(output, indent=4)
initial_prices_formatted_cad = f"initial_pricess_format_cad = {initial_prices_cad}"

# Save the formatted output to a new Python file
with open("initial_prices.py", "w") as f:
    f.write(initial_prices_formatted_cad)
