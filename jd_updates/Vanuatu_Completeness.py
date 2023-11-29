# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 14:45:48 2023

@author: jedan
"""

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from geopandas.tools import sjoin

# Load EA and Province GeoJSON files
ea_gdf = gpd.read_file('C:/PACRIS/Vanuatu/2016_PHC_Vanuatu_EA_4326.json')
province_gdf = gpd.read_file('C:/PACRIS/Vanuatu/2016_PHC_Vanuatu_Province_4326.json')

# Load GeoPackages
vu_hhld_gdf = gpd.read_file('C:/PACRIS/Vanuatu/vu_hhld_ndspvu.gpkg')
osm_vut_gdf = gpd.read_file('C:/PACRIS/Vanuatu/osm_vut.gpkg')
vu_bldexp_gdf = gpd.read_file('C:/PACRIS/Vanuatu/vu_bldexp.gpkg')

# Reproject GeoPackages to match CRS of EA and Province GeoJSON
vu_hhld_gdf = vu_hhld_gdf.to_crs(ea_gdf.crs)
osm_vut_gdf = osm_vut_gdf.to_crs(ea_gdf.crs)
vu_bldexp_gdf = vu_bldexp_gdf.to_crs(ea_gdf.crs)

# Initialize DataFrame to store counts
ea_count_df = ea_gdf[['ea2016']].copy()
ea_count_df['ea_group'] = ea_count_df['ea2016'].str[:2]  # EA grouping based on first 2 digits


# Fill NaNs with 0
ea_count_df.fillna(0, inplace=True)


# # Perform spatial joins and count per EA for vu_hhld and osm_vut
# for gdf, name in zip([vu_hhld_gdf, osm_vut_gdf, vu_bldexp_gdf], ['vu_hhld', 'osm_vut', 'vu_bldexp']):
#     joined = sjoin(ea_gdf, gdf, how='left', predicate='contains')
#     counts = joined.groupby('ea2016').size()
#     ea_count_df[name + '_count'] = ea_count_df['ea2016'].map(counts).fillna(0)  # Fill NaNs with 0

# # Debugging: Print the first few records after the join
# print("Debug: ea_count_df after join")
# print(ea_count_df.head())

# # Count buildings using "totBuildin" for vu_bldexp
# joined_bldexp = sjoin(ea_gdf, vu_bldexp_gdf, how='left', predicate='contains')
# sum_buildings = joined_bldexp.groupby('ea2016')['totBuildin'].sum()
# ea_count_df['vu_bldexp_count'] = sum_buildings

# # Debugging information
# print("Debug: ea_count_df sample")
# print(ea_count_df.sample(5))

# # Calculate relative percentages per EA zone within each EA group
# ea_group_total = ea_count_df.groupby('ea_group').sum()

# # Debugging information
# print("Debug: ea_group_total")
# print(ea_group_total)

# ea_relative_percent_df = ea_count_df.copy()
# for col in ['vu_hhld_count', 'osm_vut_count', 'vu_bldexp_count']:
#     ea_relative_percent_df[col] = ea_count_df.apply(
#         lambda row: (row[col] / ea_group_total.loc[row['ea_group'], col]) * 100 if ea_group_total.loc[row['ea_group'], col] != 0 else 0, axis=1
#     )

# # Debugging information
# print("Debug: ea_relative_percent_df sample")
# print(ea_relative_percent_df.sample(5))

# # Create the plot for relative percentages per EA zone within each EA group
# ax2 = ea_relative_percent_df.groupby('ea_group').mean().plot(kind='bar', figsize=(15, 7))
# plt.title('Relative Percentage of Count of Polygons per EA Group')
# plt.xlabel('EA Group')
# plt.ylabel('Relative Percentage (%)')
# plt.legend(title='GeoPackages')

# plt.show()






# Perform spatial joins and count per EA for vu_hhld and osm_vut
for gdf, name in zip([vu_hhld_gdf, osm_vut_gdf], ['vu_hhld', 'osm_vut']):
    joined = sjoin(ea_gdf, gdf, how='left', predicate='contains')
    counts = joined.groupby('ea2016').size()
    ea_count_df[name + '_count'] = ea_count_df['ea2016'].map(counts).fillna(0)  # Fill NaNs with 0

# Count buildings using "totBuildin" for vu_bldexp and update ea_count_df
joined_bldexp = sjoin(ea_gdf, vu_bldexp_gdf, how='left', predicate='contains')
sum_buildings = joined_bldexp.groupby('ea2016')['totBuildin'].sum().fillna(0)
ea_count_df['vu_bldexp_count'] = ea_count_df['ea2016'].map(sum_buildings).fillna(0)

# Calculate relative percentages per EA zone within each EA group
ea_group_total = ea_count_df.groupby('ea_group').sum()

ea_relative_percent_df = ea_count_df.copy()
for col in ['vu_hhld_count', 'osm_vut_count', 'vu_bldexp_count']:
    ea_relative_percent_df[col] = ea_count_df.apply(
        lambda row: (row[col] / ea_group_total.loc[row['ea_group'], col]) * 100 if ea_group_total.loc[row['ea_group'], col] != 0 else 0, axis=1
    )

# Create the plot for relative percentages per EA zone within each EA group
ax2 = ea_relative_percent_df.plot(x='ea2016', y=['vu_hhld_count', 'osm_vut_count', 'vu_bldexp_count'], kind='bar', figsize=(15, 7))
plt.title('Relative Percentage of Count of Polygons per EA Group')
plt.xlabel('EA Group')
plt.ylabel('Relative Percentage (%)')
plt.legend(title='GeoPackages')

plt.show()



# Calculate the sum per EA group
ea_group_total = ea_count_df.groupby('ea_group').sum()

# Calculate the relative percentages per EA zone within each EA group
ea_relative_percent_df = ea_count_df.copy()

for col in ['vu_hhld_count', 'osm_vut_count', 'vu_bldexp_count']:
    ea_relative_percent_df[col] = ea_count_df.apply(
        lambda row: (row[col] / ea_group_total.loc[row['ea_group'], col]) * 100 if ea_group_total.loc[row['ea_group'], col] != 0 else 0, axis=1
    )

# Create the plot for relative percentages per EA group
ax2 = ea_relative_percent_df.groupby('ea_group').mean()[['vu_hhld_count', 'osm_vut_count', 'vu_bldexp_count']].plot(kind='bar', figsize=(15, 7))
plt.title('Relative Percentage of Count of Polygons per EA Group')
plt.xlabel('EA Group')
plt.ylabel('Relative Percentage (%)')
plt.legend(title='GeoPackages')

plt.show()



# Perform spatial joins and count per EA for vu_hhld and osm_vut
for gdf, name in zip([vu_hhld_gdf, osm_vut_gdf], ['vu_hhld', 'osm_vut']):
    joined = sjoin(ea_gdf, gdf, how='left', predicate='contains')
    counts = joined.groupby('ea2016').size()
    ea_count_df[name + '_count'] = counts

# Sum of "Floor_Area" per province for vu_bldexp
joined_vu_bldexp = sjoin(province_gdf, vu_bldexp_gdf, how='left', predicate='contains')
joined_vu_bldexp['TotalFloorArea'] = joined_vu_bldexp['FloorArea'] * joined_vu_bldexp['totBuildin']


# Check if 'Floor_Area' column exists
if 'FloorArea' in joined_vu_bldexp.columns:
    sum_floor_area = joined_vu_bldexp.groupby('pname')['TotalFloorArea'].sum()
else:
    print("Warning: 'Floor_Area' column not found in vu_bldexp. Skipping this calculation.")
    sum_floor_area = pd.Series(0, index=province_gdf['pname'].unique())





# Merge counts back to original EA GeoDataFrame and save to new GeoPackage
ea_gdf = ea_gdf.merge(ea_count_df, on='ea2016', how='left')
ea_gdf.to_file('C:/PACRIS/Vanuatu/Enumeration_Area_Statistics.gpkg', driver='GPKG')

# Generate comparison plot for all 6 provinces
province_count_df = pd.DataFrame(index=province_gdf['pname'].unique())

for gdf, name in zip([vu_hhld_gdf, osm_vut_gdf, vu_bldexp_gdf], ['vu_hhld', 'osm_vut', 'vu_bldexp']):
    joined = sjoin(province_gdf, gdf, how='left', predicate='contains')
    if name == 'vu_bldexp':
        counts = joined.groupby('pname')['totBuildin'].sum()
    else:
        counts = joined.groupby('pname').size()
    province_count_df[name] = counts

# Relative percentages
province_percent_df = (province_count_df / province_count_df.sum()) * 100

# Create the plot
ax1 = province_percent_df.T.plot(kind='bar', stacked=True, figsize=(15, 7))
plt.title('Relative Percentage of Count of Polygons per GeoPackage')
plt.xlabel('GeoPackage')
plt.ylabel('Relative Percentage (%)')
plt.legend(title='Province')

# Annotate with counts
for i, value in enumerate(province_count_df.sum()):
    plt.text(i, 100, f'Total: {value}', ha='center')

plt.show()



# Sum of "Floor_Area" per province for vu_bldexp
joined_vu_bldexp = sjoin(province_gdf, vu_bldexp_gdf, how='left', predicate='contains')
sum_floor_area = joined_vu_bldexp.groupby('pname')['TotalFloorArea'].sum()

# Sum of areas of OSM footprints per province
osm_vut_gdf['footprint_area'] = osm_vut_gdf.to_crs(epsg=3395)['geometry'].area
joined_osm = sjoin(province_gdf, osm_vut_gdf, how='left', predicate='contains')
sum_osm_area = joined_osm.groupby('pname')['footprint_area'].sum()

# Create DataFrame for side-by-side plot
area_df = pd.DataFrame({
    'vu_bldexp_Floor_Area': sum_floor_area,
    'osm_footprint_area': sum_osm_area
})

# Create the side-by-side plot
ax3 = area_df.plot(kind='bar', figsize=(15, 7))
plt.title('Sum of Floor_Area and Footprint Area per Province')
plt.xlabel('Province')
plt.ylabel('Area (square meters)')
plt.legend(title='Data Source')

plt.show()
