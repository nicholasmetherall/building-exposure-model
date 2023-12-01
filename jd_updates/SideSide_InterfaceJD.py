# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 22:02:48 2023

@author: jedan
"""

import tkinter as tk
from tkinter import filedialog, ttk
import geopandas as gpd
from time import time
import folium
from tkinter import messagebox
from io import BytesIO
from PIL import Image, ImageTk
import webview

def create_map(boundary_file):
    ea_gdf = gpd.read_file(boundary_file)
    
    # Print CRS for debugging
    print(f"Original CRS: {ea_gdf.crs}")
    
    # Convert to EPSG:3857 if it's not already in that CRS
    if ea_gdf.crs != "EPSG:4326":
        ea_gdf = ea_gdf.to_crs("EPSG:4326")
    
    # Print new CRS for debugging
    print(f"New CRS: {ea_gdf.crs}")
    
    # Calculate and print centroid for debugging
    centroid = [ea_gdf.geometry.centroid.y.mean(), ea_gdf.geometry.centroid.x.mean()]
    print(f"Calculated centroid: {centroid}")
    
    m = folium.Map(location=centroid, zoom_start=10)
    
    # Print geometry for debugging
    print(ea_gdf.geometry.head())
    
    folium.GeoJson(ea_gdf.to_json()).add_to(m)
    m.save("map.html")

def show_map():
    boundary_file = boundary_file_entry.get()
    create_map(boundary_file)
    
    # Open a new window to display the map
    webview.create_window('Map', 'map.html')
    webview.start()

def process_data():
    # Read user inputs from Tkinter widgets
    boundary_file = boundary_file_entry.get()
    osm_file = osm_file_entry.get()
    pcrafi1_file = pcrafi1_file_entry.get()
    pcrafi2_file = pcrafi2_file_entry.get()
    iso_code = iso_code_entry.get()
    use_vu_hhld = vu_hhld_check_var.get()
    
    # Load EA Boundaries
    print("Loading EA Boundaries...")
    start_time = time()
    ea_gdf = gpd.read_file(boundary_file)
    print(f"Loaded EA Boundaries in {time() - start_time:.2f} seconds.")
    
    # Initialize empty DataFrame to store results
    result_df = ea_gdf[['geometry']].copy()
    
    # Process vut_osm
    print("Processing OSM data...")
    start_time = time()
    vut_osm_gdf = gpd.read_file(osm_file)
    vut_osm_gdf['area_sqm'] = vut_osm_gdf['geometry'].to_crs(epsg=3395).area  # Converting to EPSG:3395 for area calculation in square meters
    joined_vut_osm = gpd.sjoin(vut_osm_gdf, ea_gdf, how="inner", op='within', predicate='within')
    result_df['vut_sum_area'] = joined_vut_osm.groupby('index_right')['area_sqm'].sum()
    result_df['vut_osm_ct'] = joined_vut_osm.groupby('index_right').size()
    result_df['vut_osm_avg'] = result_df['vut_sum_area'] / result_df['vut_osm_ct']
    print(f"Processed vut_osm in {time() - start_time:.2f} seconds.")
    
    if use_vu_hhld:
        # Process vu_hhld
        print("Processing vu_hhld...")
        start_time = time()
        vu_hhld_gdf = gpd.read_file("C:/PACRIS/SideSide/VUT_HHLD/vu_hhld_ndspvu.gpkg")
        joined_vu_hhld = gpd.sjoin(vu_hhld_gdf, ea_gdf, how="inner", op='within')
        result_df['vu_hhld_ct'] = joined_vu_hhld.groupby('index_right').size()
        # Summing different wall and roof type combinations
        for name, group in joined_vu_hhld.groupby(['Roof Material', 'Wall Material']):
            short_name = f"hhld_{'_'.join(name)}"
            result_df[short_name] = group.groupby('index_right').size()
        print(f"Processed vu_hhld_ndspvu in {time() - start_time:.2f} seconds.")
    
    # Process PCRAFI I
    print("Processing PCRAFI I...")
    start_time = time()
    pcrafi1_gdf = gpd.read_file(pcrafi1_file)
    joined_pcrafi1 = gpd.sjoin(pcrafi1_gdf, ea_gdf, how="inner", op='within')

    # Calculations for PCRAFI I
    result_df['P1_Bld_Ct'] = joined_pcrafi1.groupby('index_right')['totBuildin'].sum()
    result_df['P1_FLAREA'] = joined_pcrafi1.groupby('index_right').apply(lambda x: (x['FloorArea'] * x['TotBuildin']).sum())
    result_df['P1_BltArea'] = joined_pcrafi1.groupby('index_right').apply(lambda x: (x['FloorArea'] * x['TotBuildin'] * x['NumStories']).sum())

    # Summing up the built area per combination of "NumStories, MainOcc and Const"
    for name, group in joined_pcrafi1.groupby(['NumStories', 'MainOcc', 'Const']):
        field_name = f"P1_BltArea_{'_'.join(map(str, name))}"
        result_df[field_name] = group.groupby('index_right').apply(lambda x: (x['FloorArea'] * x['TotBuildin'] * x['NumStories']).sum())

    # Summing up the value per combination of "NumStories, MainOcc and Const"
    for name, group in joined_pcrafi1.groupby(['NumStories', 'MainOcc', 'Const']):
        field_name = f"P1_Value_{'_'.join(map(str, name))}"
        result_df[field_name] = group.groupby('index_right')['Value'].sum()

    # Calculating the Average Built m2 value per type
    for name, group in joined_pcrafi1.groupby(['NumStories', 'MainOcc', 'Const']):
        field_name = f"P1_AvgM2_{'_'.join(map(str, name))}"
        weighted_avg = (group['Value'] / (group['TotBuildin'] * group['NumStories'] * group['FloorArea'])).mean()
        result_df[field_name] = weighted_avg

    print(f"Processed PCRAFI I in {time() - start_time:.2f} seconds.")
    
    # Process PCRAFI II
    print("Processing PCRAFI II...")
    start_time = time()
    pcrafi2_gdf = gpd.read_file(pcrafi2_file)
    joined_pcrafi2 = gpd.sjoin(pcrafi2_gdf, ea_gdf, how="inner", op='within')

    # Calculating the Built Area in "AREA_SQM" by combination of Usage, Wall_Mtrls, and ("STOREYS" if greater than 0; otherwise "LEVELS").
    for name, group in joined_pcrafi2.groupby(['USAGE', 'WALL_MTRLS', 'STOREYS', 'LEVELS']):
        storey_or_level = 'STOREYS' if name[2] > 0 else 'LEVELS'
        field_name = f"P2_BltArea_{'_'.join(map(str, [name[0], name[1], storey_or_level]))}"
        result_df[field_name] = group.groupby('index_right')['AREA_SQM'].sum()

    print(f"Processed PCRAFI II in {time() - start_time:.2f} seconds.")
    
    # Construct the output filename based on ISO code
    output_filename = f"C:/PACRIS/Results/{iso_code}_SideSide_Bldg_EA"
    
    # Save results
    result_df.to_file(f"{output_filename}.gpkg", driver="GPKG")
    result_df.drop(columns=['geometry']).to_csv(f"{output_filename}.csv", index=False)

    if messagebox.askyesno("Confirm", "Do you wish to exit?"):
            root.destroy()

# Initialize Tkinter
root = tk.Tk()
root.title("Geospatial Data Processor")

# Boundary file
tk.Label(root, text="Boundary File:").grid(row=0, column=0)
boundary_file_entry = tk.Entry(root)
boundary_file_entry.grid(row=0, column=1)
tk.Button(root, text="Browse", command=lambda: boundary_file_entry.insert(0, filedialog.askopenfilename())).grid(row=0, column=2)

# OSM file
tk.Label(root, text="OSM File:").grid(row=1, column=0)
osm_file_entry = tk.Entry(root)
osm_file_entry.grid(row=1, column=1)
tk.Button(root, text="Browse", command=lambda: osm_file_entry.insert(0, filedialog.askopenfilename())).grid(row=1, column=2)

# PCRAFI1 file
tk.Label(root, text="PCRAFI1 File:").grid(row=2, column=0)
pcrafi1_file_entry = tk.Entry(root)
pcrafi1_file_entry.grid(row=2, column=1)
tk.Button(root, text="Browse", command=lambda: pcrafi1_file_entry.insert(0, filedialog.askopenfilename())).grid(row=2, column=2)

# PCRAFI2 file
tk.Label(root, text="PCRAFI2 File:").grid(row=3, column=0)
pcrafi2_file_entry = tk.Entry(root)
pcrafi2_file_entry.grid(row=3, column=1)
tk.Button(root, text="Browse", command=lambda: pcrafi2_file_entry.insert(0, filedialog.askopenfilename())).grid(row=3, column=2)

# ISO code
tk.Label(root, text="ISO Code:").grid(row=4, column=0)
iso_code_entry = tk.Entry(root)
iso_code_entry.grid(row=4, column=1)

# Use vu_hhld´
vu_hhld_check_var = tk.IntVar()
tk.Checkbutton(root, text="Use vu_hhld", variable=vu_hhld_check_var).grid(row=5, columnspan=3)

# Use OSM
use_osm_check_var = tk.IntVar()
tk.Checkbutton(root, text="Use OSM", variable=use_osm_check_var).grid(row=6, columnspan=3)

# Use PCRAFI I
use_pcrafi1_check_var = tk.IntVar()
tk.Checkbutton(root, text="Use PCRAFI I", variable=use_pcrafi1_check_var).grid(row=7, columnspan=3)

# Use PCRAFI II
use_pcrafi2_check_var = tk.IntVar()
tk.Checkbutton(root, text="Use PCRAFI II", variable=use_pcrafi2_check_var).grid(row=8, columnspan=3)

# Add a button to show the map
tk.Button(root, text="Show Map", command=show_map).grid(row=10, columnspan=3)

# Process button
tk.Button(root, text="Process Data", command=process_data).grid(row=11, columnspan=3)

# Run the Tkinter event loop
root.mainloop()