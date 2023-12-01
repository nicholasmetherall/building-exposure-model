# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 07:42:33 2023

@author: jedan
"""

# Import required libraries
import geopandas as gpd
import pandas as pd
from time import time

# Load EA Boundaries
print("Loading EA Boundaries...")
start_time = time()
ea_gdf = gpd.read_file("C:/PACRIS/Vanuatu/2016_PHC_Vanuatu_EA_4326.json")
print(f"Loaded EA Boundaries in {time() - start_time:.2f} seconds.")

# Initialize empty DataFrame to store results
result_df = ea_gdf[['geometry']].copy()

# ----- Process vut_osm -----
print("Processing vut_osm...")
start_time = time()
vut_osm_gdf = gpd.read_file("C:/PACRIS/SideSide/OSM/Vanuatu/vut_osm_buildings_out.gpkg")
vut_osm_gdf['area_sqm'] = vut_osm_gdf.to_crs(epsg=3395).geometry.area  # Converting to EPSG:3395 for area calculation in square meters
joined_vut_osm = gpd.sjoin(vut_osm_gdf, ea_gdf, how="inner", predicate='within')
result_df['vut_sum_area'] = joined_vut_osm.groupby('index_right')['area_sqm'].sum()
result_df['vut_osm_ct'] = joined_vut_osm.groupby('index_right').size()
result_df['vut_osm_avg'] = result_df['vut_sum_area'] / result_df['vut_osm_ct']
print(f"Processed vut_osm in {time() - start_time:.2f} seconds.")

# ----- Process vu_hhld_ndspvu -----

# ----- Process vu_hhld_ndspvu -----
print("Processing vu_hhld_ndspvu...")
start_time = time()
vu_hhld_gdf = gpd.read_file("C:/PACRIS/SideSide/VUT-HHLD/vu_hhld_ndspvu.gpkg")
joined_vu_hhld = gpd.sjoin(vu_hhld_gdf, ea_gdf, how="inner", op='within')
result_df['vu_hhld_ct'] = joined_vu_hhld.groupby('index_right').size()
# Summing different wall and roof type combinations
for name, group in joined_vu_hhld.groupby(['Roof Material', 'Wall Material']):
    short_name = f"hhld_{'_'.join(name)}"
    result_df[short_name] = group.groupby('index_right').size()
print(f"Processed vu_hhld_ndspvu in {time() - start_time:.2f} seconds.")


# ----- Process PCRAFI I -----

# ----- Process PCRAFI I -----
print("Processing PCRAFI I...")
start_time = time()
pcrafi1_gdf = gpd.read_file("C:/PACRIS/SideSide/PCRAFI1/vu_bldexp_out.gpkg")
joined_pcrafi1 = gpd.sjoin(pcrafi1_gdf, ea_gdf, how="inner", op='within')

# Calculations for PCRAFI I
result_df['P1_Bld_Ct'] = joined_pcrafi1.groupby('index_right')['totBuildin'].sum()
result_df['P1_FLAREA'] = joined_pcrafi1.groupby('index_right').apply(lambda x: (x['FloorArea'] * x['totBuildin']).sum())
result_df['P1_BltArea'] = joined_pcrafi1.groupby('index_right').apply(lambda x: (x['FloorArea'] * x['totBuildin'] * x['NumStories']).sum())

# Summing up the built area per combination of "NumStories, MainOcc and Const"
for name, group in joined_pcrafi1.groupby(['NumStories', 'MainOcc', 'Const']):
    field_name = f"P1_BltArea_{'_'.join(map(str, name))}"
    result_df[field_name] = group.groupby('index_right').apply(lambda x: (x['FloorArea'] * x['totBuildin'] * x['NumStories']).sum())

# Summing up the value per combination of "NumStories, MainOcc and Const"
for name, group in joined_pcrafi1.groupby(['NumStories', 'MainOcc', 'Const']):
    field_name = f"P1_Value_{'_'.join(map(str, name))}"
    result_df[field_name] = group.groupby('index_right')['Value'].sum()

# Calculating the Average Built m2 value per type
for name, group in joined_pcrafi1.groupby(['NumStories', 'MainOcc', 'Const']):
    field_name = f"P1_AvgM2_{'_'.join(map(str, name))}"
    weighted_avg = (group['Value'] / (group['totBuildin'] * group['NumStories'] * group['FloorArea'])).mean()
    result_df[field_name] = weighted_avg

print(f"Processed PCRAFI I in {time() - start_time:.2f} seconds.")


# ----- Process PCRAFI II -----

# ----- Process PCRAFI II -----
print("Processing PCRAFI II...")
start_time = time()
pcrafi2_gdf = gpd.read_file("C:/PACRIS/SideSide/PCRAFI2/PCRAFI_II_VUT_BuildingPolygons.gpkg")
joined_pcrafi2 = gpd.sjoin(pcrafi2_gdf, ea_gdf, how="inner", op='within')

# Calculating the Built Area in "AREA_SQM" by combination of Usage, Wall_Mtrls, and ("STOREYS" if greater than 0; otherwise "LEVELS").
for name, group in joined_pcrafi2.groupby(['USAGE', 'WALL_MTRLS', 'STOREYS', 'LEVELS']):
    storey_or_level = 'STOREYS' if name[2] > 0 else 'LEVELS'
    field_name = f"P2_BltArea_{'_'.join(map(str, [name[0], name[1], storey_or_level]))}"
    result_df[field_name] = group.groupby('index_right')['AREA_SQM'].sum()

print(f"Processed PCRAFI II in {time() - start_time:.2f} seconds.")

# Save results
result_df.to_file("C:/PACRIS/Results/VUT_SideSide_Bldg_EA.gpkg", driver="GPKG")
result_df.drop(columns=['geometry']).to_csv("C:/PACRIS/Results/VUT_SideSide_Bldg_EA.csv", index=False)