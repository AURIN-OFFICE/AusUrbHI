import os
import subprocess

# Path to your TIF files
folder_path = ("../../_data/AusUrbHI HVI data unprocessed/Geoscape/SurfaceCover_JUN23_ACTNSW_GDA94_GEOTIFF_182/"
               "Surface Cover/Surface Cover 2M JUNE 2023/Standard")

# List all TIF files in the specified directory
tif_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.tif')]

# Create a text file listing all the TIF files
list_file_path = "../../_data/AusUrbHI HVI data unprocessed/Geoscape/temporary/tif_list.txt"
with open(list_file_path, 'w') as file:
    for tif_file in tif_files:
        file.write(tif_file + '\n')

# Temporary VRT path
vrt_path = "../../_data/AusUrbHI HVI data unprocessed/Geoscape/temporary/temp.vrt"

# Output path
output_file_path = "../../_data/AusUrbHI HVI data unprocessed/Geoscape/temporary/merged_2m_surface.tif"

# GDAL tools paths
gdalbuildvrt_path = 'C:/OSGeo4W/bin/gdalbuildvrt.exe'
gdal_translate_path = 'C:/OSGeo4W/apps/Python39/Scripts/gdal_translate.exe'

# Create VRT using the list file
cmd_vrt = [gdalbuildvrt_path, '-input_file_list', list_file_path, vrt_path]
subprocess.run(cmd_vrt)

# Convert VRT to merged TIFF
cmd_merge = [gdal_translate_path, vrt_path, output_file_path]
subprocess.run(cmd_merge)
