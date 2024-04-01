import geopandas as gdp
from src.main.python.geo_data_processing import create_geo_dataframe
import sys
sys.path.append("C:/Users/Linus/PycharmProjects/BA/")


ROOT_PATH = 'C:/Users/Linus/PycharmProjects/BA/'

TEST_SHAPE_FILE = 'src/test/resources/input/Gebaut.shp'
TEST_GPKG_FILE = 'src/test/resources/input/W30.gpkg'
actual = create_geo_dataframe([ROOT_PATH + TEST_SHAPE_FILE], [ROOT_PATH + TEST_GPKG_FILE])
TEST_GDP_EXPECTED = 'src/test/resources/output/gemeinden_niedrige_Dichte_gdfs.csv'
expected = gdp.read_file(ROOT_PATH + TEST_GDP_EXPECTED, GEOM_POSSIBLE_NAMES="geometry", KEEP_GEOM_COLUMNS="NO")
actual_csv = actual.to_csv()
expected_csv = expected.to_csv()
assert(actual_csv == expected_csv)
#print("test the false case")
#expected_csv = '1'
#assert(actual_csv == expected_csv)
