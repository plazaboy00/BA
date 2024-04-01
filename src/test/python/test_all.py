import sys
sys.path.append("C:\\Users\\Linus\\PycharmProjects\\BA\\")

from src.main.python.geo_data_processing import create_geo_dataframe
import geopandas as gdp
import pandas as pd

ROOT_PATH = 'C:\\Users\\Linus\\PycharmProjects\\BA\\'

TEST_SHAPE_FILE = 'src\\test\\resources\\input\\Gebaut.shp'
TEST_GPKG_FILE = 'src\\test\\resources\\input\\W30.gpkg'
actual = create_geo_dataframe(ROOT_PATH + TEST_SHAPE_FILE, ROOT_PATH + TEST_GPKG_FILE)
TEST_GDP_EXPECTED = 'src\\test\\resources\\output\\gemeinden_niedrige_Dichte_gdfs.csv'
expected_csv = pd.read_csv(ROOT_PATH + TEST_GDP_EXPECTED)
expected = gdp.read_file(ROOT_PATH + TEST_GDP_EXPECTED, GEOM_POSSIBLE_NAMES="geometry", KEEP_GEOM_COLUMNS="NO")
print(expected_csv)

#assert actual == expected
