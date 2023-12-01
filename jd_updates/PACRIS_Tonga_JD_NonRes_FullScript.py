# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 07:49:34 2023

@author: jedan
"""

# Import required packages
import geopandas as gpd
import pandas as pd

# Read the GeoPackage file
gdf_path = 'C:/PACRIS/TON_EA_Joined3.gpkg'
gdf = gpd.read_file(gdf_path)

# Read labor statistics from RelativePercentageEmployeeNonRes_Tonga.xlsx
labor_stats_df = pd.read_excel('C:/PACRIS/RelativePercentageEmployeeNonRes_Tonga.xlsx')

# Extract total number of employed people for each location
total_employees_by_location = labor_stats_df.iloc[0, 1:].to_dict()

# Calculate the total population for each island
total_population_by_island = gdf.groupby('ADM1_NAME')['EA_POP2'].sum().reset_index()

# Define function to calculate the number of employees in each sector
def calculate_num_employees(row, location):
    total_employees = total_employees_by_location[location]
    total_population_island = total_population_by_island.loc[total_population_by_island['ADM1_NAME'] == row['ADM1_NAME'], 'EA_POP2'].values[0]
    return (row['EA_POP2'] / total_population_island) * total_employees

# Initialize a DataFrame for 'Tongatapu'
tongatapu_df = gdf[gdf['ADM1_NAME'] == 'Tongatapu'].copy()
total_population_tongatapu = tongatapu_df['EA_POP2'].sum()

# Generate the _NUMEMP columns without the Urban or Rural suffix
for sector in list(labor_stats_df['Male'][1:]):
    for location in ['Tongatapu Urban', 'Tongatapu Rural']:
        col_name = f'{sector}_NUMEMP'
        percentage_employed_in_sector = labor_stats_df.loc[labor_stats_df['Male'] == sector, location].values[0] / 100
        tongatapu_df[col_name] = tongatapu_df.apply(lambda row: calculate_num_employees(row, location) * percentage_employed_in_sector, axis=1)


# Calculate the proportion of employees that should be in "Tongatapu Urban" - hardwired
total_urban_employees = 6871
total_rural_employees = 14534
total_employees_tongatapu = total_urban_employees + total_rural_employees
urban_employee_proportion = total_urban_employees / total_employees_tongatapu

# Sort the Tongatapu DataFrame by population density in descending order
tongatapu_df_sorted = tongatapu_df.sort_values(by='POPDENS2', ascending=False).reset_index(drop=True)

# Initialize variables to keep track of the cumulative sum of employees and population
cumulative_employees = 0
cumulative_population = 0

# Initialize lists to keep track of which EAs (now using 'blkid') are classified as "Urban" or "Rural"
urban_eas = []
rural_eas = []

# Go through each EA in Tongatapu to classify it as "Urban" or "Rural"
for index, row in tongatapu_df_sorted.iterrows():
    ea_population = row['EA_POP2']  # Update this if the population is stored in a different column
    ea_employees = sum(row[f'{sector}_NUMEMP'] for sector in list(labor_stats_df['Male'][1:]))
    
    # Check if adding this EA to "Urban" would exceed the target proportion of urban employees
    if (cumulative_employees + ea_employees) / total_employees_tongatapu <= urban_employee_proportion:
        urban_eas.append(row['blkid'])
        cumulative_employees += ea_employees
        cumulative_population += ea_population
    else:
        rural_eas.append(row['blkid'])

# Update the Tongatapu DataFrame to include a new column indicating whether each EA is "Urban" or "Rural"
tongatapu_df['Area_Type'] = tongatapu_df['blkid'].apply(lambda x: 'Urban' if x in urban_eas else 'Rural')

# Initialize a DataFrame for other islands
other_areas_df = gdf[gdf['ADM1_NAME'] != 'Tongatapu'].copy()

# Display the first few rows of the updated Tongatapu DataFrame
print(tongatapu_df.head())


# 1. Calculate the number of employees (_NUMEMP) for other islands
#    (We already did this for Tongatapu, dividing it into Urban and Rural)

for sector in list(labor_stats_df['Male'][1:]):
    for location in total_employees_by_location.keys():
        if location not in ['Tongatapu Urban', 'Tongatapu Rural']:
            col_name = f'{sector}_NUMEMP'
            percentage_employed_in_sector = labor_stats_df.loc[labor_stats_df['Male'] == sector, location].values[0] / 100
            other_areas_df[col_name] = other_areas_df.apply(lambda row: calculate_num_employees(row, location) * percentage_employed_in_sector, axis=1)

# 2. Calculate the floor area per employee (_FA_EMP)
# Read the non-residential floor area per employee data
fa_employee_df = pd.read_csv('C:/PACRIS/nonres_FAemployee_lookup_tonga2.csv')

def calculate_floor_area(row, sector):
    floor_area_per_employee = fa_employee_df.loc[fa_employee_df['Lookup'] == sector, 'NRFA x Emp (m2)'].values[0]
    
    # Check if the value can be converted to a float
    if floor_area_per_employee == '-':
        # Handle the case where the value is a dash (you can set it to 0 or some other value)
        floor_area_per_employee = 0.0
    else:
        floor_area_per_employee = float(floor_area_per_employee)  # Convert to float

    return row[f'{sector}_NUMEMP'] * floor_area_per_employee

for sector in list(labor_stats_df['Male'][1:]):
    tongatapu_df[f'{sector}_FA_EMP'] = tongatapu_df.apply(lambda row: calculate_floor_area(row, sector), axis=1)
    other_areas_df[f'{sector}_FA_EMP'] = other_areas_df.apply(lambda row: calculate_floor_area(row, sector), axis=1)

# 3. Multiply the calculated floor area by the values for non-residential areas
# (For now, using a placeholder value of $750 per m^2)
ucc_value = 400

for sector in list(labor_stats_df['Male'][1:]):
    tongatapu_df[f'{sector}_Economic_Value'] = tongatapu_df[f'{sector}_FA_EMP'] * ucc_value
    other_areas_df[f'{sector}_Economic_Value'] = other_areas_df[f'{sector}_FA_EMP'] * ucc_value

# Concatenate the Tongatapu and other areas DataFrames to get the complete DataFrame
final_df = pd.concat([tongatapu_df, other_areas_df])

# Save the results as a CSV file
final_df.to_csv('C:/PACRIS/NRES_TON_Final_Economic_Value2.csv', index=False)

# Save the updated GeoDataFrame back to a GeoPackage
final_gdf = gpd.GeoDataFrame(final_df)
final_gdf.to_file('C:/PACRIS/TON_EA_Joined3_updated2.gpkg', driver="GPKG")

