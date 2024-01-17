# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 14:32:16 2023

@author: jedan
"""

import pandas as pd
import geopandas as gpd
import os

# File paths
agriculture_data_path = "Tonga_Agriculture_CensusData_ADM3.csv"
village_census_shp_path = "TON_EA_Joined3_updated.gpkg"
unit_costs_path = "tonga_ucag_agriculture.csv"
output_csv_path = "Tonga_Agriculture_FinalExp_ADM3.csv"
output_gpkg_path = "Tonga_Agriculture_FinalExp_ADM3.gpkg"

# Load agriculture census data
agriculture_data = pd.read_csv(agriculture_data_path, encoding='ISO-8859-1')

# Load unit costs data
unit_costs = pd.read_csv(unit_costs_path, encoding='ISO-8859-1')

# Load village census shapefile
village_census = gpd.read_file(village_census_shp_path)

# Join the agriculture census data to the village census data
merged_data = village_census.merge(agriculture_data, left_on='ADM3_PCODE', right_on='JOINADM3', how='left')

# Prepare the unit costs data for easy lookup
unit_costs_dict = dict(zip(unit_costs['Type'], unit_costs['Value per unit']))

# Initialize a column to store the total value
merged_data['VAL_AG_TOT'] = 0

# Iterate through columns in the agriculture data
for column in agriculture_data.columns:
    if column.startswith(('ACRES_', 'TREES_', 'NUM_')):
        value_column_name = 'VALUE_' + column
        unit_cost = unit_costs_dict.get(column, 0)
        merged_data[value_column_name] = merged_data[column] * unit_cost
        merged_data['VAL_AG_TOT'] += merged_data[value_column_name]
    elif column.startswith('RAW_'):
        value_column_name = 'VALUE_' + column
        merged_data[value_column_name] = merged_data[column]
        merged_data['VAL_AG_TOT'] += merged_data[value_column_name]

# Save the resulting data to a CSV file
merged_data.to_csv(output_csv_path, index=False)

# Save the resulting data with the shapefile as a GeoPackage file
merged_data_excluding_fid = merged_data.drop(columns=['fid'], errors='ignore')
merged_data_excluding_fid.to_file(output_gpkg_path, driver="GPKG")

print("Process completed successfully!")
print(f"CSV output: {output_csv_path}")
print(f"GeoPackage output: {output_gpkg_path}")

merged_data_excluding_fid = merged_data.drop(columns=['fid'], errors='ignore')
merged_data_excluding_fid.to_file(output_gpkg_path, driver="GPKG")
print("Process completed successfully!")
except Exception as e:
print(f"An error occurred: {e}")
