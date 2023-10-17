import geopandas as gpd
from tqdm import tqdm
from geopandas import GeoDataFrame


class StudyAreaProcessor:
    def __init__(self, meshblock_gdf, study_area_gdf, building_gdf):
        self.meshblock_gdf = meshblock_gdf
        self.study_area_gdf = study_area_gdf
        self.building_gdf = building_gdf

    def preprocessing(self):
        # create a dictionary of SA1 area
        self.sa1_area_dict = self.study_area_gdf.set_index('SA1_CODE21')['AREASQKM21'].to_dict()

        # group buildings by SA1
        self.grouped_buildings = self.building_gdf.groupby('SA1_CODE21')
        assert len(self.grouped_buildings.groups) == len(
            self.study_area_gdf), "Number of SA1s in study area does not match number of SA1s in building data."

    def compute_fields(self):
        self.result = []
        for sa1_code, group_data in tqdm(self.grouped_buildings, total=len(self.grouped_buildings),
                                         desc="processing buildings"):
            count = len(group_data)
            sp_adj_yes = group_data['SP_ADJ'].value_counts().get('yes', 0)
            pr_rf_ma_counts = group_data['PR_RF_MA'].value_counts()

            # compute fields based on values of all buildings in the SA1
            sa1_dict = {'SA1_CODE21': sa1_code,
                        'SP_ADJ': sp_adj_yes / count,
                        'ROOF_HGT': group_data['ROOF_HGT'].mean(),
                        'MAT_Tile': pr_rf_ma_counts.get('Tile', 0) / count,
                        'MAT_Metal': pr_rf_ma_counts.get('Metal', 0) / count,
                        'MAT_Concre': pr_rf_ma_counts.get('Flat Concrete', 0) / count,
                        'AREA': group_data['AREA'].sum() / self.sa1_area_dict[sa1_code] * 1e6,
                        'EST_LEV': group_data['EST_LEV'].mean()}
            self.result.append(sa1_dict)

    def save_output(self, output_path):
        new_gdf = GeoDataFrame(self.result, crs=self.study_area_gdf.crs)
        new_gdf = new_gdf.merge(self.study_area_gdf[['SA1_CODE21', 'geometry']], on='SA1_CODE21', how='left')
        new_gdf.to_file(output_path)


if __name__ == "__main__":
    building_gdf = gpd.read_file("../_data/AusUrbHI HVI data unprocessed/Geoscape/temporary/buildings_in_study_area.shp")
    meshblock_gdf = gpd.read_file("../_data/study area/meshblock_study_area_2021.shp")
    study_area_gdf = gpd.read_file("../_data/study area/ausurbhi_study_area_2021.shp")
    print("data loaded.")

    processor = StudyAreaProcessor(meshblock_gdf, study_area_gdf, building_gdf)
    processor.preprocessing()
    print("Grouping done.")
    processor.compute_fields()
    print("Computing done.")
    processor.save_output('../_data/AusUrbHI HVI data processed/Geoscape/buildings.shp')
