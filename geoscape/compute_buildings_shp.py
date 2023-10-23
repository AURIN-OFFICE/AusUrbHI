import pandas as pd
import geopandas as gpd
from tqdm import tqdm

class StudyAreaProcessor:
    def __init__(self, meshblock_gdf, study_area_gdf, building_gdf):
        """
        Initialize the processor with meshblock, study area, and building dataframes.
        """
        self.meshblock_gdf = meshblock_gdf
        self.study_area_gdf = study_area_gdf
        self.building_gdf = building_gdf

    def preprocessing(self):
        """
        Preprocess the data: compute study area dictionary and group buildings by SA1.
        """
        # Create a dictionary of SA1 area
        self.sa1_area_dict = self.study_area_gdf.set_index('SA1_CODE21')['AREASQKM21'].to_dict()
        
        # Group buildings by SA1
        self.grouped_buildings = self.building_gdf.groupby('SA1_CODE21')
        print(f"{len(self.grouped_buildings.groups)} grouped, {len(self.study_area_gdf)} total study areas.")
    
    @staticmethod
    def compute_luminance(hex):
        """
        Compute luminance from hex code.
        """
        def hex_to_rgb(value):
            value = value.lstrip('#')
            length = len(value)
            return tuple(int(value[i:i + length // 3], 16) for i in range(0, length, length // 3))
        
        rgb = hex_to_rgb(hex)
        r, g, b = [x / 255.0 for x in rgb]
        return 0.299 * r + 0.587 * g + 0.114 * b
        
    def compute_fields(self):
        """
        Compute fields for each group of buildings.
        """
        self.results = [
            {
                'SA1_CODE21': sa1_code,
                'SP_ADJ': round(group_data['SP_ADJ'].str.contains('Yes', case=False, na=False).sum() / len(group_data), 2),
                'ROOF_HGT': round(group_data['ROOF_HGT'].mean(), 2),
                'MAT_Tile': round(group_data['PR_RF_MAT'].value_counts().get('Tile', 0) / len(group_data), 2),
                'MAT_Metal': round(group_data['PR_RF_MAT'].value_counts().get('Metal', 0) / len(group_data), 2),
                'MAT_Concre': round(group_data['PR_RF_MAT'].value_counts().get('Flat Concrete', 0) / len(group_data), 2),
                'ROOF_CLR': round(group_data['ROOF_CLR'].dropna().apply(self.compute_luminance).mean(), 2),
                'AREA': round(group_data['AREA'].sum() / (self.sa1_area_dict[sa1_code] * 1e6), 2),
                'EST_LEV': round(group_data['EST_LEV'].mean(), 2)
            }
            for sa1_code, group_data in 
            tqdm(self.grouped_buildings, total=len(self.grouped_buildings), desc="processing buildings")
        ]


    def save_output(self, output_path):
        """
        Save the results to a specified path.
        """
        result_df = pd.DataFrame(self.results)
        merged_df = result_df.merge(self.study_area_gdf[['SA1_CODE21', 'geometry']], on='SA1_CODE21', how='left')
        new_gdf = gpd.GeoDataFrame(merged_df, geometry='geometry', crs=self.study_area_gdf.crs)
        new_gdf.to_file(output_path)


if __name__ == "__main__":
    # Load data
    building_gdf = gpd.read_file("../_data/AusUrbHI HVI data unprocessed/Geoscape/temporary/buildings_in_study_area.shp")
    meshblock_gdf = gpd.read_file("../_data/study area/meshblock_study_area_2021.shp")
    study_area_gdf = gpd.read_file("../_data/study area/ausurbhi_study_area_2021.shp")
    print("Data loaded.")

    # Process data
    processor = StudyAreaProcessor(meshblock_gdf, study_area_gdf, building_gdf)
    processor.preprocessing()
    print("Grouping done.")
    processor.compute_fields()
    print("Computing done.")
    processor.save_output('../_data/AusUrbHI HVI data processed/Geoscape/buildings.shp')
