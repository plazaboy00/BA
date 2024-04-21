from bus_functions import *
from plot import *

ROOT_FILES = 'C:/Users/Linus/PycharmProjects/BA/'
ROOT_Busstations = 'src/main/resources/Buslinie/Busstationen/'

#Pfad zur Shapefile-Datei mit den Strassen
ROOT_RESOURCE_STRASSENNETZ = 'src/main/resources/QGIS/Strassen/'

# Definieren des Bereichs für das Straßennetzwerk
north, south, east, west = 47.3667, 47.2586, 8.754, 8.6103

# Laden des Straßennetzwerks
G = load_street_network(north, south, east, west)

# Speichern des Straßennetzwerks als GeoPackage
save_street_network(G, ROOT_FILES + ROOT_RESOURCE_STRASSENNETZ + "OSMStrassennetz.gpkg")

# Laden der Bushaltestellen
bus_stops = gpd.read_file(ROOT_FILES + ROOT_Busstations + "Bushalte.shp")

# Hinzufügen der Rückfahrt-Haltestellen
bus_stops_with_return = add_return_trip(bus_stops)

# Konvertierung der Bushaltestellenprojektion von LV95 nach WGS84
bus_stops_with_return['geometry'] = bus_stops_with_return['geometry'].apply(lv95_to_wgs84)

# Berechnung der kürzesten Routen zwischen den Haltestellen
routes, route_lengths = compute_shortest_paths(G, bus_stops_with_return)

# Plotten der Routen auf dem Straßennetzwerk
plot_routes(G, routes)

# Berechnung der Gesamtlänge der Route
total_route_length = sum(route_lengths) / 1000
print("Gesamtlänge der Route:", total_route_length, "Kilometer")