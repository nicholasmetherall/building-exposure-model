# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 14:29:09 2023

@author: jedan
"""

import geopandas as gpd
import pandas as pd

# Define the function to calculate unit cost of construction
def calculate_unit_cost(row):
    try:
        return row['Value'] / (row['totBuildin'] * row['NumStories'] * row['FloorArea'])
    except ZeroDivisionError:
        return None

# Load the to_bldexp_out Geopackage file
to_bldexp_path = 'C:/PACRIS/SideSide/PCRAFI1/to_bldexp_out.gpkg'
to_bldexp = gpd.read_file(to_bldexp_path)

# Calculate the unit cost for each row
to_bldexp['UnitCost'] = to_bldexp.apply(calculate_unit_cost, axis=1)

# Aggregate the data by Occ, Const, and NumStories to get the average FloorArea and UnitCost
aggregated_data = to_bldexp.groupby(['Occ', 'Const', 'NumStories']).agg({
    'FloorArea': 'mean',
    'UnitCost': 'mean'
}).reset_index()

# Define the path for the output CSV file
output_csv_path = 'C:/PACRIS/SideSide/PCRAFI1/PCRAFI_1_Tonga_UCCs.csv'

# Export the aggregated data to a CSV file
aggregated_data.to_csv(output_csv_path, index=False)

print(f"Aggregated data has been saved to {output_csv_path}")


import geopandas as gpd
import pandas as pd

# Load the PCRAFI_II_TON_BuildingPolygons and PCRAFI_II_TON_BuildingPoints Geopackage files
polygons_path = 'C:/PACRIS/SideSide/PCRAFI2/PCRAFI_II_TON_BuildingPolygons.gpkg'
points_path = 'C:/PACRIS/SideSide/PCRAFI2/PCRAFI_II_TON_BuildingPoints.gpkg'

polygons_data = gpd.read_file(polygons_path)
points_data = gpd.read_file(points_path)

# Aggregate the polygons data by Usage, Structure, and Storeys to get the average Area_sqm
aggregated_polygons = polygons_data.groupby(['Usage', 'Structure', 'Storeys']).agg({
    'Area_sqm': 'mean'
}).reset_index()

# Aggregate the points data by Usage, Structure, and Storeys to get the average Area_sqm
aggregated_points = points_data.groupby(['Usage', 'Structure', 'Storeys']).agg({
    'Area_sqm': 'mean'
}).reset_index()

# Define the paths for the output CSV files
output_csv_polygons_path = 'C:/PACRIS/SideSide/PCRAFI2/PCRAFI_II_TON_Polygons_Avg.csv'
output_csv_points_path = 'C:/PACRIS/SideSide/PCRAFI2/PCRAFI_II_TON_Points_Avg.csv'

# Export the aggregated data to CSV files
aggregated_polygons.to_csv(output_csv_polygons_path, index=False)
aggregated_points.to_csv(output_csv_points_path, index=False)

print(f"Aggregated polygons data has been saved to {output_csv_polygons_path}")
print(f"Aggregated points data has been saved to {output_csv_points_path}")
