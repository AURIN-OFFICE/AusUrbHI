import os
import subprocess

# Path to your TIF files
folder_path = "../../_data/AusUrbHI HVI data unprocessed/Geoscape/SurfaceCover_JUN23_ACTNSW_GDA94_GEOTIFF_182/Surface Cover/Surface Cover 2M JUNE 2023/Standard"

# Output path
output_file_path = "../../_data/AusUrbHI HVI data unprocessed/Geoscape/temporary/merged_2m_surface.tif"

# List all TIF files in the folder
tif_files = [f for f in os.listdir(folder_path) if f.endswith('.tif')]

# Construct the gdal_merge command
cmd = ["gdal_merge.py", "-o", os.path.abspath(output_file_path)] + tif_files

# Execute the command within the folder_path directory
subprocess.run(cmd, cwd=folder_path)
