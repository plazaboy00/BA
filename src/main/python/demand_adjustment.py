import pandas as pd

from geo_data_processing import filter_data, filter_and_calculate_traffic_data, berechne_verkehrsaufkommen


# Erstelle Root zum Hauptordner
ROOT_FILES = 'C:/Users/Linus/PycharmProjects/BA/'
ROOT_RESOURCE = 'src/main/resources/QGIS/Nutzungsplan/'
shapefile_paths = [ROOT_FILES + 'src/test/resources/input/Gebaut.shp', 'C:/Users/Linus/Documents/W1Gebaut.shp']
# Füge die verschiedene aus dem Inputornder Geo Files zusammen und speichere sie als gdf


#Importiere die Datensätze für das Verkehrsmodell, das Strassenetz und der Gemeindengrenzen
ROOT_RESOURCE_VERKEHRSMODELL = 'src/main/resources/Verkehrsmodell/'
DATEN_VERKEHRSMODELL = pd.read_csv(ROOT_FILES + ROOT_RESOURCE_VERKEHRSMODELL + 'KTZH_00001982_00003903(1).csv')

Anzahl_Meilen_Egg_oev = filter_and_calculate_traffic_data(
    DATEN_VERKEHRSMODELL, 'Meilen', 'Egg', 'oev', 2018, 'Verkehrsaufkommen'
)
Anzahl_Meilen_Egg_miv = filter_and_calculate_traffic_data(
    DATEN_VERKEHRSMODELL, 'Meilen', 'Egg', 'miv', 2018, 'Verkehrsaufkommen'
)
modal_split_oev_Oetwil = filter_and_calculate_traffic_data(
    DATEN_VERKEHRSMODELL, 'Oetwil am See', 'Männedorf', 'oev', 2018, 'Modal Split'
)

neues_verkehrsaufkommen_oev_Meilen_Egg = berechne_verkehrsaufkommen(
    Anzahl_Meilen_Egg_oev, Anzahl_Meilen_Egg_miv, modal_split_oev_Oetwil)

