# TODO 1: Importiere die benötigten Bibliotheken
import numpy as np
import geopandas as gpd
import pandas as pd


def create_geo_dataframe(geo_files):
    result = []
    for geo_file in geo_files:
        shapefile_path = ROOT_FILES + ROOT_RESOURCE + geo_file
        result.append(gpd.read_file(shapefile_path))

    return result



