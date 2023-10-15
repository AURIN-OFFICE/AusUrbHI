import xarray as xr
import os

# Define the path to the folder containing the files
folder_path = '..\\_data\\AusUrbHI HVI data unprocessed\\Longpaddock SILO LST\\'

# Define the filenames and corresponding prefixes for renaming
files_and_prefixes = [
    ('EHF_heatwaves____daily_filled.nc', 'ehf'),
    ('tn90pct_heatwaves____daily_filled.nc', 'tn'),
    ('tx90pct_heatwaves____daily_filled.nc', 'tx')
]

# Open the files using xarray and rename the variables
datasets = []
for file, prefix in files_and_prefixes:
    ds = xr.open_dataset(os.path.join(folder_path, file))
    ds = ds.rename_vars({'ends': prefix + 'end',
                         'event': prefix + 'evt'})
    if prefix == 'tn':
        ds = ds.rename_vars({'tn90pct': 'tn'})
    elif prefix == 'tx':
        ds = ds.rename_vars({'tx90pct': 'tx'})
    datasets.append(ds)

# Merge the datasets
merged_dataset = xr.merge(datasets)

# Define the output filename
output_file = os.path.join(folder_path, 'merged_heatwaves.nc')

# Save the merged dataset to a new NetCDF file
merged_dataset.to_netcdf(output_file)

print(f"Merged files saved to {output_file}")
