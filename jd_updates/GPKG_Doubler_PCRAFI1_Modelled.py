# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 13:47:24 2023

@author: jedan
"""

import geopandas as gpd

def process_geopackage(input_file_path, output_file_path):
    # Load the GeoPackage file
    gdf = gpd.read_file(input_file_path)

    # Duplicate rows based on the totBuildin value
    gdf_duplicated = gdf.loc[gdf.index.repeat(gdf['totBuildin'].astype(int))]

    # Reset index after duplication
    gdf_duplicated = gdf_duplicated.reset_index(drop=True)

    # Add new column for Value divided by totBuildin
    gdf_duplicated['Value_div_totBuildin'] = gdf_duplicated['Value'] / gdf_duplicated['totBuildin']

    # Calculate sums
    sum_value = gdf_duplicated['Value'].sum()
    sum_value_div_totBuildin = gdf_duplicated['Value_div_totBuildin'].sum()

    # Save to new GeoPackage file
    gdf_duplicated.to_file(output_file_path, driver="GPKG")

    # Output the sums
    print("Sum of Value: ", sum_value)
    print("Sum of Value divided by totBuildin: ", sum_value_div_totBuildin)

if __name__ == "__main__":
    input_path = "C:/PACRIS/SideSide/PCRAFI1/to_bldexp_out.gpkg"
    output_path = "C:/PACRIS/SideSide/PCRAFI1/to_bldexp_out_modelled_multbuildings.gpkg"
    process_geopackage(input_path, output_path)