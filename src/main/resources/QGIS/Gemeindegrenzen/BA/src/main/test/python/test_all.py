import sys
sys.path.append("C:\\Users\\Linus\\Documents\\BA\\")
from src.main.python.geo_data_processing import create_geo_dataframe
import numpy as np
import geopandas as gdp
import pandas as pd
import os

ROOT_PATH = 'C:\\Users\\Linus\\Documents\\BA\\'

TEST_SHAPE_FILE = 'src\\main\\test\\resources\\input\\Gebaut.shp'
TEST_GPKG_FILE = 'src\\main\\test\\resources\\input\\W30.gpkg'
actual = create_geo_dataframe(ROOT_PATH + TEST_SHAPE_FILE, ROOT_PATH + TEST_GPKG_FILE)
TEST_GDP_EXPECTED = 'src\\main\\test\\resources\\output\\gemeinden_niedrige_Dichte_gdfs.csv'
expected_csv = pd.read_csv(ROOT_PATH + TEST_GDP_EXPECTED)
expected = gdp.read_file(ROOT_PATH + TEST_GDP_EXPECTED)
print(expected_csv)

#assert actual == expected
