from bus_functions import *
from plot import *

def busline():
    ROOT_FILES = 'C:/Users/Linus/PycharmProjects/BA/'
    ROOT_DOCS = 'src/main/resources/Dokumente/'
    ROOT_Busstations = 'src/main/resources/Buslinie/Busstationen/'

    # Lade und die Gemeindegrenzen
    shp_file = ROOT_FILES + 'src/main/resources/QGIS/Gemeindegrenzen/Grenzen_komp.shp'
    gemeindegrenzen = gpd.read_file(shp_file)

    # Pfad zur Shapefile-Datei mit den Strassen
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
    bus_stops_with_return_wgs84 = bus_stops_with_return.copy()
    bus_stops_with_return_wgs84['geometry'] = bus_stops_with_return_wgs84['geometry'].apply(lv95_to_wgs84)

    # Berechnung der kürzesten Routen zwischen den Haltestellen
    routes, route_lengths = compute_shortest_paths(G, bus_stops_with_return_wgs84)

    # Plotten der Routen auf dem Straßennetzwerk
    #plot_routes(G, routes)


    file_path_demand = ROOT_FILES + ROOT_DOCS + "Nachfrage.geojson"
    file_path_destination = ROOT_FILES + ROOT_DOCS + "Ziele.geojson"
    demand_geojson = load_geojson(file_path_demand)
    destination_geojson = load_geojson(file_path_destination)

    passengers_gdf = passengers_on_bus(bus_stops_with_return, demand_geojson, destination_geojson)

    #plot_passengers(passengers_gdf, bus_stops_with_return, demand_geojson, destination_geojson, gemeindegrenzen)

    # Berechnung der Gesamtlänge der Route
    total_route_length = sum(route_lengths) / 1000
    print("Gesamtlänge der Route:", total_route_length, "Kilometer")
    # Gib die Anzahl Passagiere zurück
    num_passengers = count_passengers(passengers_gdf)
    print("Anzahl der Passagiere im Bus:", num_passengers)
    travel_time_bus = 55

    return num_passengers, total_route_length, travel_time_bus
