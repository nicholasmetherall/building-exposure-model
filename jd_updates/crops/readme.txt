
import pandas as pd
import geopandas as gpd

# File paths
agriculture_data_path = "Tonga_Agriculture_CensusData_ADM3.csv"
village_census_shp_path = "TON_EA_Joined3_updated.gpkg"
unit_costs_path = "tonga_ucag_agriculture.csv"
output_csv_path = "Tonga_Agriculture_FinalExp_ADM3_x.csv"
output_gpkg_path = "Tonga_Agriculture_FinalExp_ADM3_x.gpkg"

def rename_duplicates(old_columns):
    counts = {}
    new_columns = []
    for col in old_columns:
        if col in counts:
            counts[col] += 1
            new_col = f"{col}_{counts[col]}"
            new_columns.append(new_col)
        else:
            counts[col] = 0
            new_columns.append(col)
    return new_columns   

try:
    # Load agriculture census data
    # Load the data
    agriculture_data = pd.read_csv(agriculture_data_path, encoding='ISO-8859-1')
    unit_costs = pd.read_csv(unit_costs_path, encoding='ISO-8859-1')
    village_census = gpd.read_file(village_census_shp_path)
    
    # Rename 'VID' column in agriculture_data to avoid duplicates
    agriculture_data = agriculture_data.rename(columns={'VID': 'VID_agriculture'})
    agriculture_data = agriculture_data.rename(columns={'DVID': 'DVID_agriculture'})
    agriculture_data = agriculture_data.rename(columns={'Area': 'Area_agriculture'})
    
    # Merge the dataframes
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

    # Identify and rename duplicate columns
 

    merged_data.columns = rename_duplicates(merged_data.columns)

    # Check and fix invalid geometries if they exist
    merged_data['geometry'] = merged_data['geometry'].apply(lambda geom: geom if geom.is_valid else None)

    # Drop rows with invalid geometries
    merged_data = merged_data.dropna(subset=['geometry'])

    # Save the resulting data with the shapefile as a GeoPackage file
    merged_data_excluding_fid = merged_data.drop(columns=['fid'], errors='ignore')
    merged_data_excluding_fid.to_file(output_gpkg_path, driver="GPKG")

    print("Process completed successfully!")
    print(f"GeoPackage output: {output_gpkg_path}")

except Exception as e:
    print(f"An error occurred: {e}")
