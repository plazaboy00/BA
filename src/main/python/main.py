import numpy as np
import geopandas as gpd
import pandas as pd
from src.main.python.geo_data_processing import create_geo_dataframe

# Erstelle Root zum Hauptordner
ROOT_FILES = 'C:/Users/Linus/PycharmProjects/BA/'
ROOT_RESOURCE = 'src/test/resources/input/'
shapefile_paths = [ROOT_FILES + 'src/test/resources/input/Gebaut.shp', 'C:/Users/Linus/Documents/W1Gebaut.shp']
# Füge die verschiedene aus dem Inputornder Geo Files zusammen und speichere sie als gdf

gemeinden_gdfs = []
geo_files_tief = ['Gebaut.shp', 'W1Gebaut.shp', 'W30.gpkg', 'W2Uster.gpkg']
geo_files_hoch = ['W2Gebaut.gpkg', 'W2.gpkg', 'W3Uster.gpkg', 'W60.gpkg']
geo_files_zentral = ['Zentrum&Gewerbe.shp', 'ZonenOe.shp', 'Zentrum.gpkg', 'ZentrumUster.gpkg', 'ZentrumEgg.gpkg']

gdf_tiefe_Dichte = create_geo_dataframe(geo_files_tief)
gdf_hohe_Dichte = create_geo_dataframe(geo_files_hoch)
gdf_zentrale_Dichte = create_geo_dataframe(geo_files_zentral)