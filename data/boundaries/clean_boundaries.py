"""Make cmr_adm2_58.geojson from the original geoBoundaries file.

The original file has 60 rows for 58 departments, because Ndian and
Sanaga-Maritime are stored as two separate pieces each. This script merges
them, so the result has one row per department.

How to run it:

    python clean_boundaries.py ORIGINAL_FILE OUTPUT_FILE

Example:

    python clean_boundaries.py geoBoundaries-CMR-ADM2.geojson cmr_adm2_58.geojson

The original file is geoBoundaries-CMR-ADM2.geojson (the full version, not
the simplified one), downloaded from
https://data.humdata.org/dataset/geoboundaries-admin-boundaries-for-cameroon
"""

import sys

import geopandas as gpd

# the two file paths come from the command line
original_file = sys.argv[1]
output_file = sys.argv[2]

# read the original file: 60 rows
gdf = gpd.read_file(original_file)
print("rows in the original file:", len(gdf))

# merge the rows that have the same department name into one shape: 58 rows
gdf58 = gdf.dissolve(by="shapeName")

# after dissolve, shapeName is the row label; make it a normal column again
gdf58 = gdf58.reset_index()

# keep only the department name and the shape
gdf58 = gdf58[["shapeName", "geometry"]]
print("rows after merging:", len(gdf58))

# save the cleaned file
gdf58.to_file(output_file, driver="GeoJSON")
print("saved:", output_file)
