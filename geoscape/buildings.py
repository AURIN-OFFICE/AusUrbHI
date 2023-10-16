import geopandas as gpd
import pandas as pd
import fiona
from tqdm import tqdm


class StudyAreaProcessor:
    def __init__(self, building_path, meshblock_path, study_area_path, rows=None):
        self.meshblock_gdf = gpd.read_file(meshblock_path)
        print("Meshblock data loaded.")

        self.study_area_gdf = gpd.read_file(study_area_path)
        print("Study area data loaded.")

        if rows:
            with fiona.open(building_path) as source:
                features_subset = [next(iter(source)) for _ in range(rows)]
            self.building_gdf = gpd.GeoDataFrame.from_features(features_subset, crs=source.crs)
        else:
            self.building_gdf = gpd.read_file(building_path)
        print("Building data loaded.")

        self.study_buildings_data_dict = {}

    def _aggregate_buildings(self):
        meshblock_sa1_code_dict = self.meshblock_gdf.set_index('MB_CODE21')['SA1_CODE21'].to_dict()
        grouped = self.building_gdf.groupby(self.building_gdf["MB_CODE"].map(meshblock_sa1_code_dict))
        for column in ["SP_ADJ", "ROOF_HGT", "PR_RF_MAT", "AREA", "EST_LEV"]:
            self.study_buildings_data_dict[column] = grouped[column].apply(
                lambda x: [item for item in list(x) if item is not None and item == item and item != '']).to_dict()
        print("Aggregation of buildings is done.")

    def _compute_shapefile_fields_for_sa1(self, sa1_range):
        sa1_df = self.study_area_gdf.iloc[sa1_range].copy()

        sa1_df['SP_ADJ'] = sa1_df['SA1_CODE21'].apply(
            lambda x: self.study_buildings_data_dict['SP_ADJ'][x].count('yes') / len(
                self.study_buildings_data_dict['SP_ADJ'][x]) if x in self.study_buildings_data_dict['SP_ADJ'] else 0)

        sa1_df['ROOF_HGT'] = sa1_df['SA1_CODE21'].apply(
            lambda x: sum(map(float, self.study_buildings_data_dict['ROOF_HGT'][x])) / len(
                self.study_buildings_data_dict['ROOF_HGT'][x]) if x in self.study_buildings_data_dict[
                'ROOF_HGT'] else 0)

        for mat, col in [("Tile", "MAT_Tile"), ("Metal", "MAT_Metal"), ("Flat Concrete", "MAT_Concre")]:
            sa1_df[col] = sa1_df['SA1_CODE21'].apply(
                lambda x: self.study_buildings_data_dict['PR_RF_MAT'][x].count(mat) / len(
                    self.study_buildings_data_dict['PR_RF_MAT'][x]) if x in self.study_buildings_data_dict[
                    'PR_RF_MAT'] else 0)

        sa1_df['AREA'] = sa1_df.apply(
            lambda row: sum(map(float, self.study_buildings_data_dict['AREA'][row['SA1_CODE21']])) / (
                        row['AREASQKM21'] * 1e6) if row['SA1_CODE21'] in self.study_buildings_data_dict['AREA'] else 0,
            axis=1)

        sa1_df['EST_LEV'] = sa1_df['SA1_CODE21'].apply(
            lambda x: sum(self.study_buildings_data_dict['EST_LEV'][x]) / len(
                self.study_buildings_data_dict['EST_LEV'][x]) if x in self.study_buildings_data_dict['EST_LEV'] else 0)

        return sa1_df

    def _compute_shapefile_fields(self):
        dfs = []
        sa1_size = 100  # you can adjust this as needed
        total_sa1s = (len(self.study_area_gdf) + sa1_size - 1) // sa1_size

        for i in tqdm(range(total_sa1s)):
            start_idx = i * sa1_size
            end_idx = min((i + 1) * sa1_size, len(self.study_area_gdf))
            dfs.append(self._compute_shapefile_fields_for_sa1(range(start_idx, end_idx)))

        print("Shapefile field computation is done.")
        return pd.concat(dfs, ignore_index=True)

    def save_shapefile(self, output_path):
        self._aggregate_buildings()
        result_gdf = self._compute_shapefile_fields()
        result_gdf = result_gdf[
            ['geometry', 'SA1_CODE21', 'SP_ADJ', 'ROOF_HGT', 'MAT_Tile',
             'MAT_Metal', 'MAT_Concre', 'AREA', 'EST_LEV']]
        result_gdf.to_file(output_path)
        print("Shapefile saved.")


if __name__ == "__main__":
    processor = StudyAreaProcessor(
        # building_path="../_data/AusUrbHI HVI data processed/Geoscape/temporary/buildings_in_study_area.shp"
        building_path="../_data/AusUrbHI HVI data unprocessed/Geospace/Buildings_JUN23_NSW_GDA94_SHP_317/Buildings/"
                      "Buildings JUNE 2023/Standard/nsw_buildings.shp",
        meshblock_path="../_data/study area/meshblock_study_area_2021.shp",
        study_area_path="../_data/study area/ausurbhi_study_area_2021.shp",
        rows=100000
    )
    processor.save_shapefile('../_data/AusUrbHI HVI data processed/Geoscape/buildings.shp')
