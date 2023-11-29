# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 09:15:40 2023

@author: jedan
"""

import geopandas as gpd
import pandas as pd

# Load the .gpkg file
gpkg_file_path = 'C:/PACRIS/Tonga_Res_Join.gpkg'
zones_gpkg = gpd.read_file(gpkg_file_path)

# Load the area_table_tonga.csv
area_table_path = 'C:/PACRIS/area_table_tonga.csv'
area_table = pd.read_csv(area_table_path)

# Load the avg_storey_tonga.csv
avg_storey_path = 'C:/PACRIS/avg_storey_tonga.csv'
avg_storey = pd.read_csv(avg_storey_path)

# Load the urbrur_tonga.csv
urbrur_path = 'C:/PACRIS/urbrur_tonga.csv'
urbrur = pd.read_csv(urbrur_path)

# Load the ucc_table_tonga.csv
ucc_table_path = 'C:/PACRIS/ucc_table_tonga.csv'
ucc_table = pd.read_csv(ucc_table_path)

# Merge urbrur and avg_storey into zones_gpkg based on the zone code
zones_gpkg = pd.merge(zones_gpkg, urbrur, how='left', on='ADM3_PCODE')
#zones_gpkg = pd.merge(zones_gpkg, avg_storey, how='left', left_on='ADM3_PCODE', right_on='ADM3_PCODE')

# Extract column names that have "A_" as the prefix, indicating the number of buildings for each type
building_columns = [col for col in zones_gpkg.columns if col.startswith("A_")]

# Calculate the floor area for each building type and add as new columns
for col in building_columns:
    building_type = col.split("A_")[-1]
    if building_type in area_table['Class'].values:
        area = area_table.loc[area_table['Class'] == building_type, 'Urban'].values[0]
        for area_type, pct_col in zip(['Urban', 'Peri-Urban', 'Rural'], ['URB_PCT', 'PUR_PCT', 'RUR_PCT']):
            avg_storey_value = avg_storey.loc[avg_storey['Class'] == building_type, area_type].values[0]
            zones_gpkg[f"FloorArea_{building_type}_{area_type}"] = (
                zones_gpkg[col] * area * avg_storey_value * zones_gpkg[pct_col] / 100
            )

# Calculate the final building values without multiplying by the number of buildings
for col in building_columns:
    building_type = col.split("A_")[-1]
    if (building_type in area_table['Class'].values) and (building_type in ucc_table['Class'].values):
        unit_cost = ucc_table.loc[ucc_table['Class'] == building_type, 'Urban'].values[0]
        for area_type in ['Urban', 'Peri-Urban', 'Rural']:
            zones_gpkg[f"FinalValue_{building_type}_{area_type}"] = (
                zones_gpkg[f"FloorArea_{building_type}_{area_type}"] * unit_cost
            )

# Sum the total values per zone and add this as an extra column
final_value_columns = [col for col in zones_gpkg.columns if col.startswith("FinalValue_")]
zones_gpkg["TotalValue_PerZone"] = zones_gpkg[final_value_columns].sum(axis=1)

# Save the modified .gpkg file
output_directory = 'C:/PACRIS/tonga_output'
output_file_path = f"{output_directory}/Tonga_Res_Join_Modified_fixed6.gpkg"
zones_gpkg.to_file(output_file_path, driver="GPKG")
