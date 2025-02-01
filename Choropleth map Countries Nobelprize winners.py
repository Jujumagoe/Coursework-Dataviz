import json
import requests
import pandas as pd
import pycountry
import plotly.express as px
import plotly.io as pio  # You may need yo install pip install -U kaleido

# Download the JSON files
laureate_url = "https://api.nobelprize.org/v1/laureate.json"
prize_url = "https://api.nobelprize.org/v1/prize.json"

try:
    laureate_response = requests.get(laureate_url)
    laureate_response.raise_for_status()
    laureate_data = laureate_response.json()

    prize_response = requests.get(prize_url)
    prize_response.raise_for_status()
    prize_data = prize_response.json()

except requests.exceptions.RequestException as e:
    print(f"Error downloading data: {e}")
    exit()

# Extract laureate IDs from prize data
prize_laureate_ids = set()
for prize in prize_data['prizes']:
    if 'laureates' in prize:
        for laureate in prize['laureates']:
            prize_laureate_ids.add(laureate['id'])

# Filter laureate data
filtered_laureates = []
for laureate in laureate_data['laureates']:
    if laureate['id'] in prize_laureate_ids:
        filtered_laureates.append(laureate)

# Count country occurrences and store country codes
country_counts = {}
country_codes = {}

for laureate in filtered_laureates:
    if 'bornCountry' in laureate and 'bornCountryCode' in laureate:
        country = laureate['bornCountry']
        country_code = laureate['bornCountryCode']

        # Handle cases where a country is renamed (e.g., "Prussia (now Germany)")
        if "(now " in country:
            country = country.split("(now ")[1].split(")")[0]

        country_counts[country] = country_counts.get(country, 0) + 1
        country_codes[country] = country_code  # Store corresponding country codes

# Create DataFrame for plotting
country_df = pd.DataFrame({
    'country': country_counts.keys(),
    'count': country_counts.values(),
    'bornCountryCode': [country_codes[country] for country in country_counts.keys()]
})

# Function to convert ISO-2 to ISO-3
def convert_iso2_to_iso3(iso2_code):
    try:
        return pycountry.countries.get(alpha_2=iso2_code).alpha_3
    except AttributeError:
        return None  # Handle missing codes

# Apply conversion
country_df["iso_alpha"] = country_df["bornCountryCode"].apply(convert_iso2_to_iso3)
# Plot the map
fig = px.choropleth(country_df, 
                     locations='iso_alpha',  # Use ISO Alpha-3 codes
                     locationmode='ISO-3',
                     color='count', 
                     hover_name='country',
                     hover_data={'count': True, 'iso_alpha': False},
                     title='Number of Nobel Prize Winners by Country of Birth',
                     color_continuous_scale="PiYG")

# Save in pdf
pio.write_image(fig, "nobel_laureates.pdf", format="pdf")
# Save in html
fig.write_html("nobel_laureates.html")
fig.show()

