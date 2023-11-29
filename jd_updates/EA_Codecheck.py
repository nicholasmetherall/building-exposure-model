# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 13:54:17 2023

@author: jedan
"""

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from geopandas.tools import sjoin

# Load EA and Province GeoJSON files
ea_gdf = gpd.read_file('C:/PACRIS/Vanuatu/2016_PHC_Vanuatu_EA_4326.json')
province_gdf = gpd.read_file('C:/PACRIS/Vanuatu/2016_PHC_Vanuatu_Province_4326.json')

# Harmonize CRS
ea_gdf = ea_gdf.to_crs("EPSG:3395")
province_gdf = province_gdf.to_crs("EPSG:3395")

# Load GeoPackages
vu_hhld_gdf = gpd.read_file('C:/PACRIS/Vanuatu/vu_hhld_ndspvu.gpkg').to_crs("EPSG:3395")
osm_vut_gdf = gpd.read_file('C:/PACRIS/Vanuatu/osm_vut.gpkg').to_crs("EPSG:3395")
vu_bldexp_gdf = gpd.read_file('C:/PACRIS/Vanuatu/vu_bldexp.gpkg').to_crs("EPSG:3395")

# Initialize an empty DataFrame to store counts
ea_count_df = ea_gdf[['ea2016']].copy()

# Perform spatial joins and count per EA for each GeoPackage
for gdf, name in zip([vu_hhld_gdf, osm_vut_gdf, vu_bldexp_gdf], ['vu_hhld', 'osm_vut', 'vu_bldexp']):
    joined = sjoin(ea_gdf, gdf, how='left', predicate='contains')
    counts = joined.groupby('ea2016').size()
    ea_count_df[name + '_count'] = counts

# Calculate total area of buildings per EA for vu_bldexp in square meters
vu_bldexp_gdf['area_sqm'] = vu_bldexp_gdf['geometry'].area
joined_area = sjoin(ea_gdf, vu_bldexp_gdf, how='left', predicate='contains')
total_area = joined_area.groupby('ea2016')['area_sqm'].sum()
ea_count_df['vu_bldexp_area_sqm'] = total_area

# Merge the counts and areas back into the original EA GeoDataFrame
ea_gdf = ea_gdf.merge(ea_count_df, on='ea2016', how='left')

# Save the updated EA GeoDataFrame to a new GeoPackage
ea_gdf.to_file('C:/PACRIS/Vanuatu/Enumeration_Area_Statistics.gpkg', driver='GPKG')

# Generate comparison plot for all 6 provinces
province_count_df = province_gdf[['pname']].copy()
province_count_df.set_index('pname', inplace=True)

for gdf, name in zip([vu_hhld_gdf, osm_vut_gdf, vu_bldexp_gdf], ['vu_hhld', 'osm_vut', 'vu_bldexp']):
    joined = sjoin(province_gdf, gdf, how='left', op='contains')
    counts = joined.groupby('pname').size()
    province_count_df[name + '_count'] = counts

# Calculate relative percentages
province_count_df = (province_count_df / province_count_df.sum()) * 100

# Create stacked bar chart
ax = province_count_df.plot(kind='bar', stacked=True, figsize=(15, 7))
plt.title('Relative Percentage of Count of Polygons per Province')
plt.xlabel('Province')
plt.ylabel('Relative Percentage (%)')
plt.legend(title='GeoPackages')
plt.show()