from ODPT_functions import *
from plot import *
from bus_functions import add_zones_to_gdf, calculate_income
from roadmap import load_roadmap
import os
import numpy as np


def odpt(max_capacity, max_travel_time_per_section, repetitions):
    ROOT_FILES = 'C:/Users/Linus/PycharmProjects/BA/'
    ROOT_Busstations = 'src/main/resources/Buslinie/Busstationen/'
    ROOT_odpt_stops = 'src/main/resources/ODPT/'
    ROOT_RESOURCE_STRASSENNETZ = 'src/main/resources/QGIS/Strassen/'
    ROOT_RESOURCE_STRASSENNETZGRAPH = 'src/main/resources/strassennetz/'
    strassennetz_path = os.path.join(ROOT_FILES, ROOT_RESOURCE_STRASSENNETZGRAPH, "strassenetzwerk.graphml")

    G = ox.load_graphml(strassennetz_path)

    # Pfad zur Shapefile-Datei mit den Bushaltestellen
    shapefile_path = ROOT_FILES + ROOT_odpt_stops + "ODPTSTOPS.shp"

    # Laden der Bushaltestellen als GeoDataFrame
    odpt_stops = gpd.read_file(shapefile_path)
    print(odpt_stops)

    # Füge die Rückfahrt zu den Stops
    odpt_stops_with_return = add_return_trip(odpt_stops)

    # Lade die Nachfrage und Ziel Punkte
    ROOT_DOCS = 'src/main/resources/Dokumente/'
    # file_path = ROOT_FILES + ROOT_DOCS + "Nachfrage.geojson"
    # demand_geojson = load_geojson(file_path)
    # file_path = ROOT_FILES + ROOT_DOCS + "Ziele.geojson"
    # destination_geojson = load_geojson(file_path)
    demand_file_path = ROOT_FILES + ROOT_DOCS + "Nachfrage_bahnhof.geojson"
    target_file_path = ROOT_FILES + ROOT_DOCS + "Ziele_bahnhof.geojson"
    demand_gdf = gpd.read_file(demand_file_path)
    demand_gdf_wgs84 = demand_gdf.copy()
    target_gdf = gpd.read_file(target_file_path)
    target_gdf_wgs84 = target_gdf.copy()
    # print(demand_gdf_wgs84)

    # Ändere das crs
    odpt_stops_with_return_wgs84 = odpt_stops_with_return.copy()
    odpt_stops_wgs84 = odpt_stops.copy()
    odpt_stops_with_return_wgs84['geometry'] = odpt_stops_with_return_wgs84['geometry'].apply(lv95_to_wgs84)
    odpt_stops_wgs84['geometry'] = odpt_stops_wgs84['geometry'].apply(lv95_to_wgs84)
    demand_gdf_wgs84['geometry'] = demand_gdf_wgs84['geometry'].apply(lv95_to_wgs84)
    target_gdf_wgs84['geometry'] = target_gdf_wgs84['geometry'].apply(lv95_to_wgs84)

    print('Time 1')
    # Funktion preprocess_gdfs
    demand_gdf, target_gdf, main_stops_gdf, odpt_stops_wgs84_gdf = \
        preprocess_gdfs(demand_gdf_wgs84, target_gdf_wgs84,
                        odpt_stops_with_return_wgs84, odpt_stops_wgs84, G)
    print('Time 2')
    # Sortiere, die Nachfrage punkte nach ihrer Effizienz / Entfernung
    sorted_demand_gdf, sorted_target_gdf = sort_demand_target_nodes \
        (G, demand_gdf, target_gdf, main_stops_gdf)

    print('Time 3')
    # Füge die section zu den Nachfrage- und Ziel Punkten dazu
    demand_gdf, target_gdf = add_section_to_points(G, sorted_demand_gdf, sorted_target_gdf, odpt_stops_wgs84)

    print('Time 4')
    # Sortiere die Target-Nodes in die section nach dem Demand-Node
    demand_gdf, target_gdf = sort_target_section(demand_gdf, target_gdf)

    print('Time 5')

    # Wiederhole den Prozess mehrmals
    #max_travel_time_per_section = 900  # 15 min in Sekunden
    start_timestamp = pd.Timestamp('2018-04-20 09:05:00')
    all_section_trip_points, all_successful_trips, all_passengers_gdfs = process_demand_points_repeatedly(
        demand_gdf, target_gdf, main_stops_gdf, max_travel_time_per_section, start_timestamp, max_capacity, G,
        repetitions)

    def updated_all_passenger_gdf(all_passengers_gdfs, all_section_trip_points, G):
        updated_passengers_gdfs = []
        for passengers_gdf, sorted_section_trip_points in zip(all_passengers_gdfs, all_section_trip_points):
            passengers_gdf = calculate_passenger_travel_time(sorted_section_trip_points, G, passengers_gdf)
            passengers_gdf = add_zones_to_gdf(passengers_gdf)
            passengers_gdf = calculate_income(passengers_gdf)
            updated_passengers_gdfs.append(passengers_gdf)
        return updated_passengers_gdfs


    updated_all_passenger_gdf = updated_all_passenger_gdf(all_passengers_gdfs, all_section_trip_points, G)
    print(updated_all_passenger_gdf)

    all_routes, all_total_travel_time, all_total_distance = create_sections_routes_all_passengers(
        all_section_trip_points, G)
    print(all_total_travel_time)
    print(all_total_distance)


    mean_travel_time = np.mean(all_total_travel_time)
    mean_distance = np.mean(all_total_distance)
    mean_successful_trips = np.mean(all_successful_trips)
    print('Durchschnittliche Reisezeit:', mean_travel_time, 'min')
    print('Durchschnittliche Distanz:', mean_distance, 'km')
    print('Durchschnittliche erfolgreiche Trips:', mean_successful_trips)

    return mean_successful_trips, mean_distance, mean_travel_time, updated_all_passenger_gdf



max_capacity_odpt, max_travel_time_per_section, repetitions = 5, 900, 2
odpt_passengers, odpt_km, odpt_total_travel_time, passenger_gdf = odpt(max_capacity_odpt, max_travel_time_per_section, repetitions)
