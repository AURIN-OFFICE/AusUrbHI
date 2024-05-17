import arcpy


def regularize_building_footprints(input_feature_class,
                                   output_feature_class,
                                   simplification_method="POINT_REMOVE",
                                   error_tolerance="1 Meters"):
    """
    Regularizes building footprints using the Simplify Building tool in ArcGIS Pro.

    Parameters:
    input_feature_class (str): Path to the input building footprints feature class.
    output_feature_class (str): Path to the output regularized footprints feature class.
    simplification_method (str): Method to use for simplification. Options: "POINT_REMOVE", "POINT_ANGLE",
    "PERCENT_ANGLE" (default: "POINT_REMOVE").
    error_tolerance (str): Tolerance parameter for simplification with a unit of measurement (default: "1 Meters").
    """

    arcpy.SimplifyBuilding_cartography(
        input_feature_class,
        output_feature_class,
        simplification_method,
        error_tolerance
    )


# Example usage:
input_feature_class = "output/concaved.shp"
output_feature_class = "output/regularized.shp"
simplification_method = "POINT_REMOVE"
error_tolerance = "1 Meters"

regularize_building_footprints(input_feature_class, output_feature_class, simplification_method, error_tolerance)

print("4/4 Regularization done.")

