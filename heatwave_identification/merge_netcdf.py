from netCDF4 import Dataset
import xarray as xr
import os

dir = '..\\_data\\AusUrbHI HVI data unprocessed\\Longpaddock SILO LST\\max'
nc_files = [os.path.join(dir, f) for f in os.listdir(dir) if f.endswith('.nc')]
ds = xr.concat([xr.open_dataset(f) for f in nc_files], dim='time')
ds.to_netcdf('..\\_data\\AusUrbHI HVI data unprocessed\\Longpaddock SILO LST\\max\\2015_2022_max_temp.nc')

dir = '..\\_data\\AusUrbHI HVI data unprocessed\\Longpaddock SILO LST\\min'
nc_files = [os.path.join(dir, f) for f in os.listdir(dir) if f.endswith('.nc')]
ds = xr.concat([xr.open_dataset(f) for f in nc_files], dim='time')
ds.to_netcdf('..\\_data\\AusUrbHI HVI data unprocessed\\Longpaddock SILO LST\\min\\2015_2022_min_temp.nc')

nc_file = Dataset('..\\_data\\AusUrbHI HVI data unprocessed\\Longpaddock SILO LST\\max\\2015_2022_max_temp.nc', 'r')
print(nc_file.variables.keys())
time_variable = nc_file.variables['time'][:]
max_temp_variable = nc_file.variables['max_temp'][:]
combined = list(zip(time_variable, max_temp_variable))
print(len(combined))
nc_file.close()
