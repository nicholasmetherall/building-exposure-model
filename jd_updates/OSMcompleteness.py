# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 15:11:23 2023

@author: jedan
"""

from geopandas import read_file
import matplotlib.pyplot as plt

# Load the Geopackage file
file_path = 'C:/PACRIS/Vanuatu/osm_vut.gpkg'
gdf = read_file(file_path)

# Function to plot the completeness of each field in a separate figure
def plot_single_field_completeness(gdf, field):
    non_null_count = gdf[field].count()
    null_count = len(gdf) - non_null_count
    labels = ['Non-Null', 'Null']
    sizes = [non_null_count, null_count]
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title(f'Completeness of {field} field')
    plt.show()

# Function to plot the count of unique values for each field in a separate figure
def plot_single_unique_values_count(gdf, field):
    value_counts = gdf[field].dropna().value_counts()
    plt.bar(value_counts.index, value_counts.values)
    plt.title(f'Unique Value Counts for {field}')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

# Fields to be examined
fields_to_examine = ['office', 'building', 'name', 'source']

# Generate the plots for each field in separate figures
for field in fields_to_examine:
    plot_single_field_completeness(gdf, field)
    plot_single_unique_values_count(gdf, field)
