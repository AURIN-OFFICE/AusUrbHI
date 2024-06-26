import os
import subprocess
import geopandas as gpd
import xarray as xr
from shapely.geometry import mapping
from tqdm import tqdm


class HeatNetCDFProcessor:
    """This class contains methods for processing the NetCDF files from the Longpaddock SILO LST dataset.
    """

    def __init__(self, data_folder, output_folder, study_area_shp):
        self.data_folder = data_folder
        self.output_folder = output_folder
        self.study_area_shp = study_area_shp

    def merge_raw_netcdf(self) -> None:
        """Merge the NetCDF files for each year into one file
        for each variable (maximum and minimum daily temperature)
        """
        for m in tqdm(('max', 'min'), desc="Merging raw NetCDF files", total=2):
            raw_nc_data_folder = self.data_folder + m
            nc_files = [os.path.join(raw_nc_data_folder, f)
                        for f in os.listdir(raw_nc_data_folder) if f.endswith('.nc')]

            ds = xr.concat([xr.open_dataset(f) for f in nc_files], dim='time')
            ds.to_netcdf(self.data_folder + f'2010_2022_{m}_temp.nc')

    def refine_and_buffer_netcdf(self, buff: bool = True) -> None:
        """Clip the NetCDF files to the study area, create buffer if needed, and save the result
        """
        study_area_gdf = gpd.read_file(self.study_area_shp, crs="epsg:7844")
        if buff:
            study_area_gdf = study_area_gdf.buffer(0.05)

        for m in tqdm(('max', 'min'), desc="Refining NetCDF files", total=2):
            netcdf = xr.open_dataset(self.data_folder + f'2010_2022_{m}_temp.nc')
            netcdf.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=True)
            netcdf = netcdf.rio.write_crs("EPSG:7844", inplace=True)

            clipped = netcdf.rio.clip(study_area_gdf.geometry.apply(mapping), study_area_gdf.crs)
            clipped.to_netcdf(self.output_folder + f'2010_2022_{m}_temp_clipped.nc')

    def run_ehfheatwaves_package(self) -> None:
        """Run the ehfheatwaves analysis package on the NetCDF files
        """
        cwd = os.getcwd()
        os.chdir(self.output_folder)
        command = [
            "ehfheatwaves",
            "-x", "2010_2022_max_temp_clipped.nc",
            "-n", "2010_2022_min_temp_clipped.nc",
            "--vnamex", "max_temp",
            "--vnamen", "min_temp",
            "--base", "2010-2022",
            "-p", "90",
            "-d",
            "--ehi",
            "--t90pc",
            "--tx90pc",
            "--tn90pc",
            "--tx90pc-daily",
            "--tn90pc-daily",
            "-v"
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        os.chdir(cwd)

    def fill_nan(self) -> None:
        """Fill NaN values in the analysis result NetCDF files with 0
        """
        ehfheatwaves_result_file_names = [
            "EHF_heatwaves____daily.nc",
            "tn90pct_heatwaves____daily.nc",
            "tx90pct_heatwaves____daily.nc"
        ]
        files = [self.output_folder + i for i in ehfheatwaves_result_file_names]

        for file in tqdm(files, desc="Filling NaN values", total=len(files)):
            netcdf = xr.open_dataset(file)
            netcdf = netcdf.fillna(0)
            netcdf.to_netcdf(file[:-3] + '_filled.nc')

    def merge_resulting_netcdf(self) -> None:
        """Merge all the resulting NetCDF files into one file
        """
        files_and_prefixes = [
            ('EHF_heatwaves____daily_filled.nc', 'ehf'),
            ('tn90pct_heatwaves____daily_filled.nc', 'tn'),
            ('tx90pct_heatwaves____daily_filled.nc', 'tx')
        ]
        datasets = []
        for file, prefix in tqdm(files_and_prefixes,
                                 desc="Merging resulting NetCDF files", total=len(files_and_prefixes)):
            ds = xr.open_dataset(os.path.join(self.output_folder, file))
            ds = ds.rename_vars({'ends': prefix + 'end',
                                 'event': prefix + 'evt'})
            if prefix == 'tn':
                ds = ds.rename_vars({'tn90pct': 'tn'})
            elif prefix == 'tx':
                ds = ds.rename_vars({'tx90pct': 'tx'})
            datasets.append(ds)

        merged_dataset = xr.merge(datasets)
        output_file = os.path.join(self.output_folder, 'merged_heatwaves.nc')
        merged_dataset.to_netcdf(output_file)


if __name__ == '__main__':
    processor = HeatNetCDFProcessor(
        '../_data/AusUrbHI HVI data unprocessed/Longpaddock SILO LST/',
        '../_data/AusUrbHI HVI data unprocessed/Longpaddock SILO LST/peninsula/',
        '../_data/study area/SA1_PeninsulaHealth_2021.shp')
    # processor.merge_raw_netcdf()
    processor.refine_and_buffer_netcdf()
    processor.run_ehfheatwaves_package()
    # processor.fill_nan()
    # processor.merge_resulting_netcdf()
