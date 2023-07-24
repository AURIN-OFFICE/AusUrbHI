import numpy as np
import xarray as xr


def calculate_EHF(max_temp_file, min_temp_file):
    # Load the netCDF files
    max_temp_ds = xr.open_dataset(max_temp_file)
    min_temp_ds = xr.open_dataset(min_temp_file)

    # Extract the temperature variables
    # Replace 'temperature' with the actual name of the temperature variable in your datasets
    max_temp = max_temp_ds['max_temp']
    min_temp = min_temp_ds['min_temp']

    # Calculate daily mean temperature
    DMT = (max_temp + min_temp) / 2

    # Calculate the 95th percentile of DMT
    T95 = np.percentile(DMT, 95)

    # Calculate the 3-day average of DMT
    TDP = DMT.rolling(time=3).mean()

    # Calculate the significance index
    EHIsig = TDP - T95

    # Calculate the acclimatisation index
    EHFaccl = TDP - DMT.rolling(time=30).mean()

    # Calculate the EHF
    EHF = EHIsig * np.maximum(1, EHFaccl)

    # Drop the first few days that contain NaN values
    EHF = EHF.dropna(dim='time')

    return EHF


# Replace 'max_temp.nc' and 'min_temp.nc' with your actual file paths
EHF = calculate_EHF('..\\_data\\longpaddock_silo_lst\\2016_2021_max_temp_clipped_buffered.nc',
                    '..\\_data\\longpaddock_silo_lst\\2016_2021_min_temp_clipped_buffered.nc')

EHF.to_netcdf('..\\_data\\longpaddock_silo_lst\\ehf.nc')
