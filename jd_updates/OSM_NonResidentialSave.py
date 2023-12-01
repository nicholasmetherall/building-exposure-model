# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 21:30:43 2023

@author: jedan
"""

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import geopandas as gpd
import pandas as pd

def process_data():
    filepath = filepath_entry.get()
    projection = projection_var.get()
    
    # Read the data
    buildings_gdf = gpd.read_file(filepath)
    
    # Reproject if necessary
    if projection == 'EPSG:4326':
        buildings_gdf = buildings_gdf.to_crs(epsg=3857)
        
    # Calculate the area in square meters directly from the geometry
    buildings_gdf['area_m2'] = buildings_gdf['geometry'].area
    
    # Filter the buildings based on the given criteria
    filtered_buildings = buildings_gdf[
        (buildings_gdf['area_m2'] > 500) |
        (buildings_gdf['name'].notna()) |
        (~buildings_gdf['type'].isin(['residential', 'house']) & ~pd.isna(buildings_gdf['type']))
    ]
    
    # Save only the filtered buildings to a new GeoPackage
    output_filepath = filepath.replace('.gpkg', '_filtered.gpkg').replace('.shp', '_filtered.gpkg')
    filtered_buildings.to_file(output_filepath, driver="GPKG")
    
    print(f"Filtered data saved to {output_filepath}")
    
    # Prompt to ask if the user wants to quit
    if messagebox.askyesno("Question", "Uno mas? Noch eins? Or do you want to quit now?"):
        root.quit()

# Tkinter GUI
root = tk.Tk()
root.title("Building Footprints Filter")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Filepath input
filepath_label = ttk.Label(frame, text="Filepath:")
filepath_label.grid(row=0, column=0, sticky=tk.W)
filepath_entry = ttk.Entry(frame, width=50)
filepath_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
filepath_button = ttk.Button(frame, text="Browse", command=lambda: filepath_entry.insert(0, filedialog.askopenfilename()))
filepath_button.grid(row=0, column=2, sticky=tk.W)

# Projection selection
projection_var = tk.StringVar(value='EPSG:3857')
projection_label = ttk.Label(frame, text="Projection:")
projection_label.grid(row=1, column=0, sticky=tk.W)
projection_3857 = ttk.Radiobutton(frame, text="EPSG:3857", variable=projection_var, value='EPSG:3857')
projection_3857.grid(row=1, column=1, sticky=tk.W)
projection_4326 = ttk.Radiobutton(frame, text="EPSG:4326", variable=projection_var, value='EPSG:4326')
projection_4326.grid(row=1, column=2, sticky=tk.W)

# Process button
process_button = ttk.Button(frame, text="Process", command=process_data)
process_button.grid(row=2, columnspan=3)

root.mainloop()
