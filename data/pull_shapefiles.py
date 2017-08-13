# -*- coding: utf-8 -*-
"""
Title: pull_shapefiles.py

Description: This program downloads zip folders containing the shapefiles for 
state legislative districts from the US Census Bureau.

It then unzips the folders and moves the contents into one folder so that the
shapefiles can be merged together into a single shapefile of all state
legislative districts in the US using QGIS.

Inputs:
    none
    
Outputs:
    zip folders of each state's upper and lower legislative districts
    all .cpg, .dbf, .prj, .shp, .shx and associated xml files in 
        "lowerDistricts" and "upperDistricts" folders 
    
Created on 7/18/2017

@author: Alice
"""

import os
import requests
import zipfile

os.chdir('data\State legislature shapefiles')

state_fips = ["01", "02", "04", "05", "06", "08", "09",
              "10", "11", "12", "13", "15", "16", "17", "18", "19",
              "20", "21", "22", "23", "24", "25", "26", "27", "28", "29",
              "30", "31", "32", "33", "34", "35", "36", "37", "38", "39",
              "40", "41", "42", "44", "45", "46", "47", "48", "49", 
              "50", "51", "53", "54", "55", "56"]

# a function to download all the shape zipfiles at the specified district level
# for all states
def get_folders(level):
    for fip in state_fips:
        url = 'http://www2.census.gov/geo/tiger/GENZ2016/shp/cb_2016_{state_fip}_{district}_500k.zip'.format(state_fip=fip, district=level)
        folder_name = url.rsplit('/', 1)[1]
            
        if os.path.exists(folder_name):
            continue
        else:
            try:
                r = requests.get(url)
                open(folder_name, 'wb').write(r.content)
            except:  # because DC and Nebraska don't have lower state legislative districts
                pass
            
# get upper state legislative districts
get_folders("sldu")

# get lower state legislative districts
get_folders("sldl")

# unzip folders and place contents in the appropriate folders
for folder in os.listdir(os.getcwd()):
    if '.zip' in folder:
        zip_folder = zipfile.ZipFile(folder)
        if 'sldu' in folder:
            zip_folder.extractall(os.path.join('upperDistricts'))
        else:
            zip_folder.extractall(os.path.join('lowerDistricts'))
        zip_folder.close()
