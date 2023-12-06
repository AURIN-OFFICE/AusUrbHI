from typing import List
from shapely.geometry import Polygon, MultiPolygon
import geopandas as gpd


class BuildingReBuffer:
    """
    A class to perform rebuffering on building polygons in a shapefile.
    """

    def __init__(self, input_shapefile: str):
        """
        Initializes the BuildingBuffer object with the input shapefile.

        Parameters:
        input_shapefile (str): Path to the input shapefile containing building polygons.
        """
        self.data = gpd.read_file(input_shapefile)
        self.multipolygon = self.data.geometry.tolist()

    def apply_buffer(self, buff: float = 1.2) -> List[Polygon]:
        """
        Applies buffering to the building polygons.

        Parameters:
        buff (float): Buffer distance for the building polygons (default: 1.2).

        Returns:
        List[Polygon]: A list of buffered building polygons.
        """
        new_polygons = []
        for polygon in self.multipolygon:
            try:
                new_polygons.append(polygon.buffer(buff).buffer(-buff))
            except AttributeError:  # multipolygon
                for sub_polygon in list(polygon.geoms):
                    new_polygons.append(sub_polygon.buffer(buff).buffer(-buff))
        return new_polygons

    @staticmethod
    def save_buffered_polygons(buffered_polygons: List[Polygon], output_shapefile: str):
        """
        Saves the buffered polygons to a new shapefile.

        Parameters:
        buffered_polygons (List[Polygon]): A list of buffered building polygons.
        output_shapefile (str): Path to the output shapefile.
        """
        new_multipolygon = MultiPolygon(buffered_polygons)
        polygons = [{'id': i, 'geometry': poly} for i, poly in enumerate(new_multipolygon.geoms)]
        gdf = gpd.GeoDataFrame(polygons)
        gdf.to_file(output_shapefile)


# Example usage:
input_shapefile = "output/concaved.shp"
output_shapefile = "output/rebuffered.shp"
buff = 1.2

building_buffer = BuildingReBuffer(input_shapefile)
buffered_polygons = building_buffer.apply_buffer(buff)
building_buffer.save_buffered_polygons(buffered_polygons, output_shapefile)

print("3/4 Rebuffer done.")

