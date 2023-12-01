# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 14:24:49 2023

@author: jedan
"""

import geopandas as gpd
import pandas as pd
import fiona
from shapely.geometry import Polygon

# Load the geopackage and shapefile
geopackage_path = 'C:/PACRIS/Chosen Admins/TongaEA.gpkg'
shapefile_path = 'C:/PACRIS/SideSide/OSM/Tonga/ton_roads_free_1.shp'
geopackage_layer = gpd.read_file(geopackage_path, layer='tonga_ea_pophh')
shapefile = gpd.read_file(shapefile_path)

# Reproject the datasets to EPSG:3857
target_crs = "EPSG:3857"
geopackage_layer_reprojected = geopackage_layer.to_crs(target_crs)
shapefile_reprojected = shapefile.to_crs(target_crs)

# Initialize an empty DataFrame to store the results
result_df = pd.DataFrame(columns=['blkid'] + list(shapefile['fclass'].unique()))

# Loop through each Enumeration Zone (EA)
for idx, row in geopackage_layer_reprojected.iterrows():
    blkid = row['blkid']
    ea_geom = row['geometry']
    
    # Find the roads that intersect with this EA
    intersecting_roads = shapefile_reprojected[shapefile_reprojected.intersects(ea_geom)]
    
    # Clip the roads to the EA boundary and calculate the length
    clipped_lengths = {}
    for _, road in intersecting_roads.iterrows():
        clipped_geom = road['geometry'].intersection(ea_geom)
        if isinstance(clipped_geom, Polygon):
            continue
        road_type = road['fclass']
        length = clipped_geom.length
        clipped_lengths[road_type] = clipped_lengths.get(road_type, 0) + length
    
    # Add the calculated lengths to the result DataFrame
    result_row = {'blkid': blkid, **clipped_lengths}
    result_df = result_df.append(result_row, ignore_index=True)

# Fill NaN values with 0
result_df.fillna(0, inplace=True)

# Define the unit costs per meter for each road type
unit_costs = {
    'primary': 1100,
    'primary_link': 1100,
    'primary_trunk': 1100,
    'secondary': 800,
    'secondary_link': 800,
    'secondary_trunk': 800,
    'tertiary': 250,
    'tertiary_link': 250,
    'tertiary_trunk': 250,
    'residential': 100,
}
default_unit_cost = 40

# Calculate the road value for each Enumeration Zone (EA) and road type
value_df = result_df.copy()
for road_type, unit_cost in unit_costs.items():
    if road_type in value_df.columns:
        value_df[road_type] *= unit_cost

# List of road types that actually appear in the DataFrame
available_road_types = [road_type for road_type in unit_costs.keys() if road_type in value_df.columns]

# Calculate the total road value for each Enumeration Zone (EA)
value_df['total_value'] = value_df[available_road_types].sum(axis=1)

# Calculate the value for each individual road segment
shapefile_reprojected['Road_value'] = shapefile_reprojected['fclass'].map(unit_costs).fillna(default_unit_cost) * shapefile_reprojected['length_m']

# Create a DataFrame for the unit costs
ucc_df = pd.DataFrame(list(unit_costs.items()), columns=['fclass', 'unit_cost'])

# Save the unit costs to a CSV file
ucc_csv_path = 'C:/PACRIS/Results/ucc_roads_tonga.csv'
ucc_df.to_csv(ucc_csv_path, index=False)

# Save the road values per EA to a CSV file
road_values_csv_path = 'C:/PACRIS/Results/road_values_per_EA_Tonga.csv'
value_df.to_csv(road_values_csv_path, index=False)

# Save this information in a new GeoPackage
output_geopackage_path = 'C:/PACRIS/Results/Road_Values_Tonga.gpkg'
shapefile_reprojected.to_file(output_geopackage_path, layer='road_values', driver="GPKG")
