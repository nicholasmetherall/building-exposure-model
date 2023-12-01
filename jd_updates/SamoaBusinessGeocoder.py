# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 14:06:05 2023

@author: jedan
"""

import os
import pandas as pd
from geopy.geocoders import Nominatim
from time import time

def geocode_address(address):
    geolocator = Nominatim(user_agent="myGeocoder")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

# Define the folder where the files are located
input_folder = "C:/Samoa"

# Define the output Excel file name
output_file = "Samoa Business Registry Geocoded.xlsx"

# Initialize an empty list to hold dataframes
dfs = []

# Loop through each file in the folder
for filename in os.listdir(input_folder):
    if filename.endswith('.xls'):
        full_path = os.path.join(input_folder, filename)
        df = pd.read_excel(full_path)
        dfs.append(df)

# Concatenate all the DataFrames in the list
concatenated_df = pd.concat(dfs, ignore_index=True)

# Remove duplicate rows
unique_df = concatenated_df.drop_duplicates()

print("Processing time...")
start_time = time()
# Geocode addresses in column 6
unique_df['Latitude'], unique_df['Longitude'] = zip(*unique_df.iloc[:, 5].map(geocode_address))
print(f"Processed geocoding in {time() - start_time:.2f} seconds.")

# Save the DataFrame with unique rows to an Excel file
unique_df.to_excel(os.path.join(input_folder, output_file), index=False)