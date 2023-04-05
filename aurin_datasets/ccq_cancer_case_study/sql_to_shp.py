import os
import geopandas as gpd
from sqlalchemy import create_engine


def convert_sql_to_shp(directory,
                       db_connection_string,
                       output_directory):
    # Create a connection to the database
    engine = create_engine(db_connection_string)

    # Iterate through all files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.sql'):
            file_path = os.path.join(directory, filename)

            # Read SQL file
            with open(file_path, 'r') as file:
                sql_query = file.read()

            # Execute the SQL query and read the result into a GeoDataFrame
            gdf = gpd.read_postgis(sql=sql_query, con=engine.connect())
            print(gdf.head())
            print('test')

            # Export the GeoDataFrame to a shapefile
            output_file = os.path.join(output_directory, f'{os.path.splitext(filename)[0]}.shp')
            gdf.to_file(output_file)

        break


if __name__ == "__main__":
    directory = 'db-office_dumps_qld'
    db_connection_string = ''
    output_directory = 'ccq_qld_data_shp'

    convert_sql_to_shp(directory, db_connection_string, output_directory)
