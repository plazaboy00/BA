from bus_functions import *
from plot import *
import os
from roadmap import load_roadmap
#from scenario import start_timestamp, end_timestamp

def busline(max_capacity, waiting_time):
    ROOT_FILES = 'C:/Users/Linus/PycharmProjects/BA/'
    ROOT_DOCS = 'src/main/resources/Dokumente/'
    ROOT_Busstations = 'src/main/resources/Buslinie/Busstationen/'
    ROOT_RESOURCE_STRASSENNETZGRAPH = 'src/main/resources/strassennetz/'
    strassennetz_path = os.path.join(ROOT_FILES, ROOT_RESOURCE_STRASSENNETZGRAPH, "strassenetzwerk.graphml")

    G = ox.load_graphml(strassennetz_path)
    # Lade und die Gemeindegrenzen

    # Pfad zur Shapefile-Datei mit den Strassen
    ROOT_RESOURCE_STRASSENNETZ = 'src/main/resources/QGIS/Strassen/'

    # Laden der Bushaltestellen
    bus_stops = gpd.read_file(ROOT_FILES + ROOT_Busstations + "Bushalte.shp")

    # Hinzufügen der Rückfahrt-Haltestellen
    bus_stops_with_return = add_return_trip(bus_stops)

    # Bestimme Abfahrtszeit der Busse
    start_timestamp = pd.Timestamp('2018-04-20 09:05:00')

    # Konvertierung der Bushaltestellenprojektion von LV95 nach WGS84
    bus_stops_with_return_wgs84 = bus_stops_with_return.copy()
    bus_stops_with_return_wgs84['geometry'] = bus_stops_with_return_wgs84['geometry'].apply(lv95_to_wgs84)

    # Berechnung der kürzesten Routen zwischen den Haltestellen
    routes, route_lengths, busstops_with_time = compute_shortest_paths(G, bus_stops_with_return_wgs84, start_timestamp, waiting_time)

    # print(busstops_with_time)

    bus_stops_with_return['ankunftszeit'] = busstops_with_time['ankunftszeit']
    # print(bus_stops_with_return)

    # Plotten der Routen auf dem Straßennetzwerk
    # plot_routes(G, routes)

    file_path_demand = ROOT_FILES + ROOT_DOCS + "Nachfrage_bahnhof.geojson"
    file_path_destination = ROOT_FILES + ROOT_DOCS + "Ziele_bahnhof.geojson"
    demand_geojson = load_geojson(file_path_demand)
    destination_geojson = load_geojson(file_path_destination)

    # Bestimme die Passagiere im Bus
    passengers_gdf = passengers_on_bus(bus_stops_with_return, demand_geojson, destination_geojson, max_capacity)
    # print(passengers_gdf)

    # Berechne die Reisezeit der Passagiere
    passengers_gdf = compute_travel_time(passengers_gdf)
    print(passengers_gdf)

    # Berechne die Gesamtreisezeit
    total_travel_time = compute_travel_time_bus(busstops_with_time)
    print("Die gesamte Reisezeit beträgt:", total_travel_time)
    # plot_passengers(passengers_gdf, bus_stops_with_return, demand_geojson, destination_geojson, gemeindegrenzen)

    # Berechnung der Gesamtlänge der Route
    total_route_length = sum(route_lengths) / 1000
    print("Gesamtlänge der Route:", total_route_length, "Kilometer")
    # Gib die Anzahl Passagiere zurück
    num_passengers = count_passengers(passengers_gdf)
    print("Anzahl der Passagiere im Bus:", num_passengers)

    # Füge die Anzahl an Zonen in gdf dazu
    passengers_gdf = add_zones_to_gdf(passengers_gdf)

    # Berechne die Einnahmen für jeden Passagier
    passengers_gdf = calculate_income(passengers_gdf)

    print(passengers_gdf)

    return num_passengers, total_route_length, total_travel_time, passengers_gdf

#waiting_time = 20
#max_capacity_bus = 31
#busline_passengers, busline_km, busline_total_travel_time, passenger_gdf = busline(max_capacity_bus, waiting_time)
#print(busline_km)
#print(type(busline_km))
