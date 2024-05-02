from ODPT_functions import *
from plot import *

ROOT_FILES = 'C:/Users/Linus/PycharmProjects/BA/'
ROOT_Busstations = 'src/main/resources/Buslinie/Busstationen/'
ROOT_ODPT_stops = 'src/main/resources/ODPT/'
ROOT_RESOURCE_STRASSENNETZ = 'src/main/resources/QGIS/Strassen/'

# Minimale und maximale Breite und Länge des Rechtecks
north, south, east, west = 47.3876, 47.2521, 8.754, 8.6003

# Herunterladen des Straßennetzwerks basierend auf dem Rechteck
G = ox.graph.graph_from_bbox(north, south, east, west, network_type='drive')

# Konvertieren des Graphen in ein GeoJSON-FeatureCollection
features = ox.graph_to_gdfs(G, nodes=False, edges=True)
geojson_data = features.to_json()

# Bestimmen des relativen Pfads
file_path = ROOT_FILES + ROOT_RESOURCE_STRASSENNETZ + "strassenetzwerk.geojson"

# Schreiben des GeoJSON-Daten in die Datei
with open(file_path, "w") as f:
    json.dump(geojson_data, f)

# impute edge (driving) speeds and calculate edge travel times
G = ox.speed.add_edge_speeds(G)
G = ox.speed.add_edge_travel_times(G)

# you can convert MultiDiGraph to/from GeoPandas GeoDataFrames
gdf_nodes, gdf_edges = ox.utils_graph.graph_to_gdfs(G)
G = ox.utils_graph.graph_from_gdfs(gdf_nodes, gdf_edges, graph_attrs=G.graph)
#print(G)

# Pfad zur Shapefile-Datei mit den Bushaltestellen
shapefile_path = ROOT_FILES + ROOT_ODPT_stops + "ODPTSTOPS.shp"

# Laden der Bushaltestellen als GeoDataFrame
ODPT_stops = gpd.read_file(shapefile_path)
#print(ODPT_stops)

# Füge die Rückfahrt zu den Stops
ODPT_stops_with_return = add_return_trip(ODPT_stops)

# Lade die Nachfrage und Ziel Punkte
ROOT_DOCS = 'src/main/resources/Dokumente/'
file_path = ROOT_FILES + ROOT_DOCS + "Nachfrage.geojson"
demand_geojson = load_geojson(file_path)
file_path = ROOT_FILES + ROOT_DOCS + "Ziele.geojson"
destination_geojson = load_geojson(file_path)
demand_file_path = ROOT_FILES + ROOT_DOCS + "Nachfrage.geojson"
target_file_path = ROOT_FILES + ROOT_DOCS + "Ziele.geojson"
demand_gdf = gpd.read_file(demand_file_path)
demand_gdf_wgs84 = demand_gdf.copy()
target_gdf = gpd.read_file(target_file_path)
target_gdf_wgs84 = target_gdf.copy()

# Ändere das crs
ODPT_stops_with_return_wgs84 = ODPT_stops_with_return.copy()
ODPT_stops_wgs84 = ODPT_stops.copy()
ODPT_stops_with_return_wgs84['geometry'] = ODPT_stops_with_return_wgs84['geometry'].apply(lv95_to_wgs84)
ODPT_stops_wgs84['geometry'] = ODPT_stops_wgs84['geometry'].apply(lv95_to_wgs84)
demand_gdf_wgs84['geometry'] = demand_gdf_wgs84['geometry'].apply(lv95_to_wgs84)
target_gdf_wgs84['geometry'] = target_gdf_wgs84['geometry'].apply(lv95_to_wgs84)

# Funktion preprocess_gdfs
demand_gdf, target_gdf, main_stops_gdf, ODPT_stops_wgs84_gdf = \
    preprocess_gdfs(demand_gdf_wgs84, target_gdf_wgs84,
                    ODPT_stops_with_return_wgs84, ODPT_stops_wgs84, G)

#print(target_gdf)
#print(demand_gdf)
#print(main_stops_gdf.head())

# Sortiere die Nachfragepunkte nach ihrer Effizienz / Entfernung
sorted_demand_gdf, sorted_target_gdf = sort_demand_target_nodes\
    (G, demand_gdf, target_gdf, main_stops_gdf)

# Füge die section zu den Nachfrage- und Ziel Punkten dazu
demand_gdf, target_gdf = add_section_to_points(G, sorted_demand_gdf, sorted_target_gdf, ODPT_stops_wgs84)
#print(demand_gdf.head())
#print(target_gdf.head())

sorted_section_trip_points, successful_trips = process_demand_points\
    (demand_gdf, target_gdf, main_stops_gdf, main_stops_gdf, G)
print(sorted_section_trip_points)
print(successful_trips)