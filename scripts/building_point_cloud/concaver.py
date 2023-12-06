from typing import List
from shapely.geometry import Polygon, MultiPolygon
import geopandas as gpd


class BuildingHoleRemover:
    """
    A class to remove small holes from building polygons in a shapefile.
    """

    def __init__(self, input_shapefile: str):
        """
        Initializes the BuildingHoleRemover object with the input shapefile.

        Parameters:
        input_shapefile (str): Path to the input shapefile containing building polygons.
        """
        self.data = gpd.read_file(input_shapefile)
        self.multipolygon = self.data.geometry.tolist()

    def remove_small_holes(self, min_area: float = 5.0) -> List[Polygon]:
        """
        Removes small holes from the building polygons.

        Parameters:
        min_area (float): Minimum area of the holes to be retained (default: 5.0).

        Returns:
        List[Polygon]: A list of building polygons with small holes removed.
        """
        new_polygons = []
        for polygon in self.multipolygon:
            try:
                list_interiors = []
                for interior in polygon.interiors:
                    p = Polygon(interior)
                    if p.area > min_area:
                        list_interiors.append(interior)
                temp_pol = Polygon(polygon.exterior.coords, holes=list_interiors)
                new_polygons.append(temp_pol)
            except AttributeError:  # multipolygon
                for sub_polygon in list(polygon.geoms):
                    list_interiors = []
                    for interior in sub_polygon.interiors:
                        p = Polygon(interior)
                        if p.area > min_area:
                            list_interiors.append(interior)
                    temp_pol = Polygon(sub_polygon.exterior.coords, holes=list_interiors)
                    new_polygons.append(temp_pol)
        return new_polygons

    @staticmethod
    def save_processed_polygons(processed_polygons: List[Polygon], output_shapefile: str):
        """
        Saves the processed polygons to a new shapefile.

        Parameters:
        processed_polygons (List[Polygon]): A list of processed building polygons.
        output_shapefile (str): Path to the output shapefile.
        """
        new_multipolygon = MultiPolygon(processed_polygons)
        polygons = [{'id': i, 'geometry': poly} for i, poly in enumerate(new_multipolygon.geoms)]
        gdf = gpd.GeoDataFrame(polygons)
        gdf.to_file(output_shapefile)


# Example usage:
input_shapefile = "input/buildings_raw_sv07.shp"
output_shapefile = "output/concaved.shp"
min_area = 100.0

building_hole_remover = BuildingHoleRemover(input_shapefile)
processed_polygons = building_hole_remover.remove_small_holes(min_area)
building_hole_remover.save_processed_polygons(processed_polygons, output_shapefile)

print("2/4 Concaver done.")
