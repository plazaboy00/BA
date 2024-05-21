
import numpy as np
import geopandas as gpd
import pandas as pd

def create_geo_dataframe(shapefile_paths, geopackage_paths):
    try:
        # Einzelne GeoDataFrames für jede Gemeinde erstellen und sie in einer Liste speichern
        gemeinden_gdfs = gpd.DataFrame()
        for shapefile_path in shapefile_paths:
            gemeinden_gdfs.append(gpd.read_file(shapefile_path))
        for geopackage_path in geopackage_paths:
            gemeinden_gdfs.append(gpd.read_file(geopackage_path))

        # Alle GeoDataFrames zu einem großen GeoDataFrame zusammenfügen
        gemeinden_niedrige_Dichte_gdfs = gpd.GeoDataFrame(pd.concat(gemeinden_gdfs, ignore_index=True))

        return gemeinden_niedrige_Dichte_gdfs
    except Exception as e:
        print("Fehler beim Erstellen des GeoDataFrames:", e)
        return None  # oder eine geeignete Fehlerbehandlung hier einfügen
