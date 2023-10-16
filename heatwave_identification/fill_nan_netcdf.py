import xarray as xr

nc_files = [
    "..\\_data\\AusUrbHI HVI data unprocessed\\Longpaddock SILO LST\\EHF_heatwaves____daily.nc",
    "..\\_data\\AusUrbHI HVI data unprocessed\\Longpaddock SILO LST\\tn90pct_heatwaves____daily.nc",
    "..\\_data\\AusUrbHI HVI data unprocessed\\Longpaddock SILO LST\\tx90pct_heatwaves____daily.nc"
]

# replace NaN value with zero
for nc_file in nc_files:
    netcdf = xr.open_dataset(nc_file)
    netcdf = netcdf.fillna(0)
    netcdf.to_netcdf(nc_file[:-3] + '_filled.nc')
