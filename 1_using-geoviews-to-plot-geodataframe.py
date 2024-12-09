# Author: Iman Irajian
# LinkedIn: [https://www.linkedin.com/in/imanirajian/]
# Date: 10 December, 2024

# Using GeoViews to plot GeoDataFrame
# -----------------------------------

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

from string import punctuation
punctuations = list(punctuation)
punctuations.remove(".")
punctuations.remove("-")
punctuations.remove("+")

import os

from geopy.geocoders import Nominatim
# Initialize the geolocator from geopy
geolocator = Nominatim(user_agent="tour_map")

import geopandas

from shapely.geometry import Point

import geoviews as gv
gv.extension('bokeh', 'matplotlib')
from geoviews import opts
from cartopy import crs


# 1) Read Raw Data

cities_raw = ["California", "Argentina", "TEHRAN", "    Tehran" , "       paris  ", " Rome !", "$ MaDRid", "(Berlin)", "* Marrakesh *"]


# 2) Prepare the Data

cities = []

for city_raw in cities_raw:
    value = city_raw.strip().replace("\n", "")
    for punc in punctuations:
        value = value.replace(punc, "")
    value = value.strip()
    value = value[0].upper() + value[1:].lower()
    cities.append(value)

cities = list(set(cities))

print("cities:", cities)

def reindex_df(df):
    df.reset_index(inplace = True)
    df.drop("index", axis = 1, inplace = True)

df = pd.DataFrame({"City": {}})

for city in cities:
    df.loc[len(df)] = city

df.dropna(inplace = True)
df.drop_duplicates(inplace = True)
reindex_df(df)


# 3) Define a Function to Get the Location

def get_lat_lon(city_name):
    # Initialize the geolocator
    geolocator = Nominatim(user_agent="city_locator")

    try:
        # Get the location
        location = geolocator.geocode(city_name)
        if location:
            # Return latitude and longitude
            return location.latitude, location.longitude
        else:
            print(f"City '{city_name}' not found.")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


for i, city in enumerate(df.City):
    lat_lon = get_lat_lon(city)
    if lat_lon:
        df.loc[i, "Latitude"] = lat_lon[0]
        df.loc[i, "Longitude"] = lat_lon[1]

# 4) Create a Geopandas `GeoDataFrame`

# Create geometry column with shapely Points
df['Geometry'] = df.apply(lambda x: Point((x['Latitude'], x['Longitude'])), axis=1)

# Convert to GeoDataFrame
gdf = geopandas.GeoDataFrame(df, geometry='Geometry')

# 5) Plot the Path and Stops Around the World

cities_lonlat = gv.Points(gdf, kdims=['Longitude', 'Latitude'], vdims=['City'])

(gv.tile_sources.OSM * cities_lonlat).opts(
    opts.Points(global_extent=True, width=500, height=475, size=12, color='blue')
)