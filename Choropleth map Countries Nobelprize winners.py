import json
import requests
import pandas as pd
import plotly.express as px

# Download the JSON files
laureate_url = "https://api.nobelprize.org/v1/laureate.json"
prize_url = "https://api.nobelprize.org/v1/prize.json"

try:
    laureate_response = requests.get(laureate_url)
    laureate_response.raise_for_status()  # Raise an exception for bad status codes
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

# Count country occurrences
country_counts = {}
for laureate in filtered_laureates:
    if 'bornCountry' in laureate:
        country = laureate['bornCountry'] #rules how to count the occurrences
        if "(now " in country:
            country = country.split("(now ")[1].split(")")[0]
        if "(" in country:
            country = country.split("(")[1].split(")")[0]
        if ", " in country:
            country = country.split(", ")[1]

        country_counts[country] = country_counts.get(country, 0) + 1

# Create a DataFrame for plotting
country_df = pd.DataFrame({'country': country_counts.keys(), 'count': country_counts.values()})

# Create the choropleth map
fig = px.choropleth(country_df, locations='country', locationmode='country names',
                    color='count', hover_name='country', #when hovering over generated map country & number are shown
                    title='Number of Nobel Prize Winners by Country of Birth',
                    color_continuous_scale="Viridis",
                    #projection='orthographic',
                    range_color=(1, max(country_df['count'].values)))

max_count = country_df['count'].max()
fig.update_layout(
    coloraxis_colorbar=dict(
        title=dict(text="Count"),
        tickvals=[1, max_count / 2, max_count],  # Explicitly label min, mid, max
        ticktext=["1 (Min)", f"{int(max_count / 2)} (Medium)", f"<br>{max_count} (Max)"]
    ) #<br> add some space between the title and the max label
)

#show figure
fig.show()
