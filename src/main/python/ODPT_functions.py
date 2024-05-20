import pyproj
import pandas as pd
import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt
from shapely.geometry import LineString
from shapely.ops import nearest_points
from shapely.geometry import Point
import osmnx as ox
import json
from datetime import datetime, timedelta


def add_return_trip(odpt_stops):
    # Kopiere das GeoDataFrame, um die Rückfahrt-Haltestellen hinzuzufügen
    return_trip_stops = odpt_stops.copy()

    # Entferne die Haltestelle mit der niedrigsten und höchsten ID
    return_trip_stops = return_trip_stops.iloc[:-1]

    # Kehre die Reihenfolge der Haltestellen um
    return_trip_stops = return_trip_stops.iloc[::-1]

    # Füge die Rückfahrt-Haltestellen hinzu
    odpt_stops_with_return = pd.concat([odpt_stops, return_trip_stops], ignore_index=True)

    return odpt_stops_with_return

def load_geojson(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

# LV95 Projektionsdefinition
lv95 = pyproj.Proj(init='epsg:2056')
# WGS 84 Projektionsdefinition
wgs84 = pyproj.Proj(init='epsg:4326')
# Funktion zur Umwandlung von LV95 nach WGS 84
def lv95_to_wgs84(point):
    x_lv95, y_lv95 = point.x, point.y
    x_wgs84, y_wgs84 = pyproj.transform(lv95, wgs84, x_lv95, y_lv95)
    return Point(x_wgs84, y_wgs84)


def get_nearest_node(G, point):
    nearest_node = ox.distance.nearest_nodes(G, point.x, point.y)
    return nearest_node


def preprocess_gdfs(demand_gdf, target_gdf, main_stops_gdf, odpt_stops_wgs84_gdf, graph):
    # Hinzufügen der Spalte 'nearest_node' zu den GeoDataFrames
    demand_gdf['nearest_node'] = demand_gdf['geometry'].apply(lambda point: get_nearest_node(graph, point))
    target_gdf['nearest_node'] = target_gdf['geometry'].apply(lambda point: get_nearest_node(graph, point))
    main_stops_gdf['nearest_node'] = main_stops_gdf['geometry'].apply(lambda point: get_nearest_node(graph, point))
    odpt_stops_wgs84_gdf['nearest_node'] = odpt_stops_wgs84_gdf['geometry'].apply(
        lambda point: get_nearest_node(graph, point))

    return demand_gdf, target_gdf, main_stops_gdf, odpt_stops_wgs84_gdf


def sort_demand_target_nodes(graph, demand_gdf, target_gdf, main_stops_gdf):
    # Berechne die Gesamtreisezeit für jede Zeile in demand_gdf und target_gdf
    demand_travel_times = {}
    for idx, demand_point in demand_gdf.iterrows():
        closest_main_stop = min(main_stops_gdf['nearest_node'], key=lambda x: nx.shortest_path_length(graph, demand_point['nearest_node'], x))
        demand_travel_time = nx.shortest_path_length(graph, demand_point['nearest_node'], closest_main_stop)
        demand_travel_times[idx] = demand_travel_time

    target_travel_times = {}
    for idx, target_point in target_gdf.iterrows():
        closest_main_stop = min(main_stops_gdf['nearest_node'], key=lambda x: nx.shortest_path_length(graph, target_point['nearest_node'], x))
        target_travel_time = nx.shortest_path_length(graph, target_point['nearest_node'], closest_main_stop)
        target_travel_times[idx] = target_travel_time

    # Berechne die Summe der Reisezeiten für jede Zeile in demand_gdf und target_gdf
    total_travel_times = {}
    for idx in demand_travel_times.keys():
        total_travel_times[idx] = demand_travel_times[idx] + target_travel_times[idx]

    # Sortiere die Zeilen basierend auf den Gesamtreisezeiten
    sorted_indices = sorted(total_travel_times, key=total_travel_times.get)
    sorted_demand_gdf = demand_gdf.loc[sorted_indices]
    sorted_target_gdf = target_gdf.loc[sorted_indices]

    return sorted_demand_gdf, sorted_target_gdf


def add_section_to_points(graph, demand_gdf, target_gdf, main_stops_gdf):
    # Erstelle eine leere Liste, um die Abschnitte zu speichern
    demand_sections = []
    target_sections = []

    # Iteriere über die Punkte in demand_gdf
    for idx, demand_point in demand_gdf.iterrows():
        nearest_node = demand_point['nearest_node']
        nearest_source_node = get_nearest_node(graph, demand_point.geometry)

        # Berechne die kürzeste Distanz zwischen dem Demand-Punkt und allen Haupt-Haltestellen
        distances = {}
        for stop_idx, stop in main_stops_gdf.iterrows():
            main_stop_node = get_nearest_node(graph, stop.geometry)
            shortest_distance = nx.shortest_path_length(graph, nearest_source_node, main_stop_node,
                                                        weight='travel_time')
            distances[stop_idx] = shortest_distance

        # Bestimme den nächsten und zweitnächsten Haupt-Haltestellenindex
        nearest_stop_idx = min(distances, key=distances.get)
        del distances[nearest_stop_idx]  # Entferne den nächsten Haupt-Haltestellenindex
        second_nearest_stop_idx = min(distances, key=distances.get)

        # Füge den Abschnitt hinzu
        section = (nearest_stop_idx, second_nearest_stop_idx)
        demand_sections.append(section)

    # Iteriere über die Punkte in target_gdf, falls benötigt
    for idx, target_point in target_gdf.iterrows():
        nearest_node = target_point['nearest_node']
        nearest_source_node = get_nearest_node(graph, target_point.geometry)

        # Berechne die kürzeste Distanz zwischen dem Demand-Punkt und allen Haupt-Haltestellen
        distances = {}
        for stop_idx, stop in main_stops_gdf.iterrows():
            main_stop_node = get_nearest_node(graph, stop.geometry)
            shortest_distance = nx.shortest_path_length(graph, nearest_source_node, main_stop_node,
                                                        weight='travel_time')
            distances[stop_idx] = shortest_distance

        # Bestimme den nächsten und zweitnächsten Haupt-Haltestellenindex
        nearest_stop_idx = min(distances, key=distances.get)
        del distances[nearest_stop_idx]  # Entferne den nächsten Haupt-Haltestellenindex
        second_nearest_stop_idx = min(distances, key=distances.get)

        # Füge den Abschnitt hinzu
        section = (nearest_stop_idx, second_nearest_stop_idx)
        target_sections.append(section)

    # Füge die Abschnitte den GeoDataFrames hinzu
    demand_gdf['section'] = demand_sections
    target_gdf['section'] = target_sections

    return demand_gdf, target_gdf

# Sortiere die Target-Nodes in die section nach dem Demand-Node
def sort_target_section(demand_gdf, target_gdf):
    # Iteriere über die Zeilen im demand_gdf
    for index, demand_row in demand_gdf.iterrows():
        # Holen des Abschnittswerts aus dem demand_gdf
        demand_section = demand_row['section']

        if demand_section[0] > demand_section[1]:
            demand_gdf.at[index, 'section'] = (demand_section[1], demand_section[0])

        # Holen des zugehörigen Abschnittswerts aus dem target_gdf
        target_section = target_gdf.loc[index, 'section']

        # Überprüfen, ob der erste Wert im demand größer ist als der im target
        if demand_section[0] > target_section[0]:
            # Überprüfen, ob die Reihenfolge des target-Tupels umgekehrt werden muss
            if target_section[0] < target_section[1]:
                # Umdrehen der Reihenfolge im target-Tupel
                target_gdf.at[index, 'section'] = (target_section[1], target_section[0])

        if target_section[0] == 0 and demand_section[0] != 0:
            target_gdf.at[index, 'section'] = (target_section[1], target_section[0])

    return demand_gdf, target_gdf

# Hilfsfunktionen des Models

def create_section_trip_points(df):
    section_points_lists = []
    prev_nearest_node = None

    for index, row in df.iterrows():
        current_nearest_node = row['nearest_node']
        if prev_nearest_node is not None:
            section_points_lists.append([prev_nearest_node, current_nearest_node])
        prev_nearest_node = current_nearest_node

    return section_points_lists


def add_node_to_section(start_node, target_node, demand_node, section_trip_points):
    # Durchlaufe jede Liste in der Liste
    for sublist in section_trip_points:
        # Überprüfe, ob beide Input-Elemente in der aktuellen Unterliste enthalten sind
        if start_node == sublist[0] and target_node == sublist[-1]:
            # Füge das dritte Input-Element zur Unterliste hinzu
            sublist.insert(-1, demand_node)  # Füge demand_node vor target_node ein
            return section_trip_points  # Gib die gesamte Liste zurück, nachdem das Element hinzugefügt wurde
    return section_trip_points  # Falls keine passende Unterliste gefunden wurde, gib die unveränderte Liste zurück


def sort_sublists_by_shortest_path(sorted_section_trip_points, graph):
    sorted_sublists = []

    for sublist in sorted_section_trip_points:
        start_node = sublist[0]
        end_node = sublist[-1]  # Die end_node ist der letzte Eintrag der Unterliste

        # Finde die kürzeste Pfadlänge zwischen Start- und Endknoten
        shortest_path_length = nx.shortest_path_length(graph, start_node, end_node, weight='travel_time')

        # Sortiere die restlichen Knoten basierend auf ihrer Entfernung zum Startknoten
        sorted_nodes = sorted(sublist[1:-1],
                              key=lambda x: nx.shortest_path_length(graph, start_node, x, weight='travel_time'))

        # Füge die sortierte Unterliste zur sortierten Liste hinzu
        sorted_sublist = [start_node] + sorted_nodes + [end_node]
        sorted_sublists.append(sorted_sublist)

    return sorted_sublists


def sort_sublists_by_shortest_path_with_target(sorted_section_trip_points, graph, demand_node, target_node):
    sorted_sublists = []

    for sublist in sorted_section_trip_points:
        start_node = sublist[0]
        end_node = sublist[-1]  # Die end_node ist der letzte Eintrag der Unterliste

        # Finde die kürzeste Pfadlänge zwischen Start- und Endknoten
        shortest_path_length = nx.shortest_path_length(graph, start_node, end_node, weight='travel_time')

        # Sortiere die restlichen Knoten basierend auf ihrer Entfernung zum Startknoten
        sorted_nodes = sorted(sublist[1:-1],
                              key=lambda x: nx.shortest_path_length(graph, start_node, x, weight='travel_time'))

        # Überprüfe, ob demand_node und target_node in der Liste vorhanden sind
        if demand_node in sorted_nodes and target_node in sorted_nodes:
            # Füge demand_node vor target_node ein
            sorted_nodes.insert(sorted_nodes.index(target_node), demand_node)
            sorted_nodes.insert(sorted_nodes.index(demand_node) + 1, target_node)

        # Füge die sortierte Unterliste zur sortierten Liste hinzu
        sorted_sublist = [start_node] + sorted_nodes + [end_node]
        sorted_sublists.append(sorted_sublist)

    return sorted_sublists


def calculate_travel_time_for_updated_section(demand_node, sorted_section_trip_points, graph):
    updated_section_index = None
    travel_time = 0

    # Finde den Index der aktualisierten Unterliste, die den demand_node enthält
    for i, sublist in enumerate(sorted_section_trip_points):
        if demand_node in sublist:
            updated_section_index = i
            break

    # Berechne die Reisezeit für die aktualisierte Unterliste
    if updated_section_index is not None:
        for i in range(len(sorted_section_trip_points[updated_section_index]) - 1):
            start_node = sorted_section_trip_points[updated_section_index][i]
            end_node = sorted_section_trip_points[updated_section_index][i + 1]
            travel_time += nx.shortest_path_length(graph, start_node, end_node, weight='travel_time')

    return travel_time


def calculate_travel_time_for_section_with_demand_target_nodes(sorted_section_trip_points, graph):
    travel_time = 0

    # Iteriere über jede Unterliste in sorted_section_trip_points
    for sublist in sorted_section_trip_points:
        # Iteriere über die Knoten in der Unterliste
        for i in range(len(sublist) - 1):
            start_node = sublist[i]
            end_node = sublist[i + 1]
            # Summiere die Reisezeit von start_node zu end_node
            travel_time += nx.shortest_path_length(graph, start_node, end_node, weight='travel_time')

    return travel_time


def remove_demand_node_from_sublist(start_node, target_node, demand_node, sorted_section_trip_points):
    # Iteriere über jede Unterliste in sorted_section_trip_points
    for sublist in sorted_section_trip_points:
        # Überprüfe, ob die demand_node in der Unterliste vorhanden ist
        if start_node == sublist[0] and target_node == sublist[-1] and demand_node in sublist and demand_node != \
                sublist[0] and demand_node != sublist[-1]:
            # Entferne die demand_node aus der Unterliste
            sublist.remove(demand_node)

    return sorted_section_trip_points

def validate_nodes_in_data(nodes, main_stop_nodes, passengers_gdf):
    validated_nodes = []
    for list in nodes:
        section = []
        for node in list:
            # Überprüfe, ob der Knoten in den Hauptknoten oder in den Passagieren als Ursprung oder Ziel enthalten ist
            if node in main_stop_nodes['nearest_node'].values or node in passengers_gdf['origin'].values or node in passengers_gdf['destination'].values:
                section.append(node)
        validated_nodes.append(section)

    return validated_nodes

# Hauptfunktion von odpt

def process_demand_points(demand_nodes, target_nodes, main_stop_nodes, max_travel_time_per_section, start_timestamp, G):
    successful_trips = 0
    max_capacity = 86
    passengers = []
    section_trip_points = create_section_trip_points(main_stop_nodes)
    bus_timestamp = start_timestamp

    # Iteriere über die Nachfrageknoten
    for demand_index, demand_row in demand_nodes.iterrows():

        if successful_trips == max_capacity:
            print('Fahrzeug ist voll')
            break

        demand_gemeinde = demand_row['gemeinde']
        demand_node = demand_row['nearest_node']
        demand_start_stop, demand_end_stop = demand_row['section']
        demand_timestamp = demand_row['timestamp']
        #print(demand_timestamp)

        # Suche den Start-Hauptknoten des Demand-Knotens
        demand_start_stop_row = main_stop_nodes.loc[main_stop_nodes.index == demand_start_stop]
        nearest_node_demand_start = demand_start_stop_row['nearest_node'].values[0]

        # Suche den Ziel-Hauptknoten des Demand-Knotens
        demand_end_stop_row = main_stop_nodes.loc[main_stop_nodes.index == demand_end_stop]
        nearest_node_demand_end = demand_end_stop_row['nearest_node'].values[0]

        # Füge demand_node zu den Abschnitts-Trip-Punkten hinzu
        section_trip_points = add_node_to_section(nearest_node_demand_start, nearest_node_demand_end, demand_node,
                                                  section_trip_points)
        section_trip_points = sort_sublists_by_shortest_path(section_trip_points, G)

        # Überprüfe, ob die Reisezeit pro Abschnitt die maximale Reisezeit pro Abschnitt überschreitet
        travel_time = calculate_travel_time_for_updated_section(demand_node, section_trip_points, G)
        #print(travel_time)
        if travel_time > max_travel_time_per_section:
            section_trip_points = remove_demand_node_from_sublist(nearest_node_demand_start, nearest_node_demand_end,
                                                                  demand_node, section_trip_points)
            continue

        # Überprüfe, ob der demand_node in der vorgegebenen Zeit abgeholt werden kann
        arrival_time = bus_timestamp + timedelta(seconds=travel_time)
        start_buffer = arrival_time - timedelta(minutes=10)
        end_buffer = arrival_time + timedelta(minutes=10)
        if demand_timestamp < start_buffer or demand_timestamp > end_buffer:
            section_trip_points = remove_demand_node_from_sublist(nearest_node_demand_start, nearest_node_demand_end,
                                                                  demand_node, section_trip_points)
            continue


        # Finde die zugehörigen Zielknoten für diesen Demand-Knoten
        corresponding_target_node = target_nodes.loc[
            target_nodes['passagier_nummer'] == demand_row['passagier_nummer']]
        section_tuple = corresponding_target_node['section'].values[0]
        target_start_stop, target_end_stop = section_tuple
        target_node = corresponding_target_node['nearest_node'].values[0]
        target_gemeinde = corresponding_target_node['gemeinde'].values[0]

        # Überprüfe, ob der demand und der target Knoten dieselben sind
        if demand_node == target_node:
            print('Der Demand- und Zielknoten sind identisch')
            continue

        # Suche den Start-Hauptknoten des Ziel-Knotens
        target_start_stop_row = main_stop_nodes.loc[main_stop_nodes.index == target_start_stop]
        nearest_node_target_start = target_start_stop_row['nearest_node'].values[0]

        # Suche den Ziel-Hauptknoten des Ziel-Knotens
        target_end_stop_row = main_stop_nodes.loc[main_stop_nodes.index == target_end_stop]
        nearest_node_target_end = target_end_stop_row['nearest_node'].values[0]

        section_trip_points = add_node_to_section(nearest_node_target_start, nearest_node_target_end, target_node,
                                                  section_trip_points)
        section_trip_points = sort_sublists_by_shortest_path_with_target(section_trip_points, G, demand_node,
                                                                         target_node)

        # Überprüfe, ob der target_node in der gleichen section ist wie der demand_node
        if nearest_node_demand_start == nearest_node_target_start and nearest_node_target_end == nearest_node_demand_end:
            # Berechne die Reisezeit für die aktualisierte Unterliste
            travel_time_target = calculate_travel_time_for_updated_section(target_node, section_trip_points, G)
            if travel_time_target > max_travel_time_per_section:
                section_trip_points = remove_demand_node_from_sublist(nearest_node_demand_start,
                                                                      nearest_node_demand_end, demand_node,
                                                                      section_trip_points)
                section_trip_points = remove_demand_node_from_sublist(nearest_node_target_start,
                                                                      nearest_node_target_end, target_node,
                                                                      section_trip_points)
                continue

        # Überprüfe, ob die Reisezeit pro Abschnitt die maximale Reisezeit pro Abschnitt überschreitet
        travel_time_target = calculate_travel_time_for_updated_section(target_node, section_trip_points, G)
        if travel_time_target > max_travel_time_per_section:
            section_trip_points = remove_demand_node_from_sublist(nearest_node_demand_start, nearest_node_demand_end,
                                                                  demand_node, section_trip_points)
            section_trip_points = remove_demand_node_from_sublist(nearest_node_target_start, nearest_node_target_end,
                                                                  target_node, section_trip_points)
            continue

        # Die Route zwischen Hauptknoten liegt innerhalb der Zeitbeschränkung
        successful_trips += 1
        passengers.append({
            'origin': demand_node,
            'destination': target_node,
            'id:': demand_row['passagier_nummer'] - 1,
            'start gemeinde': demand_gemeinde,
            'end gemeinde': target_gemeinde,
            'timestamp': demand_timestamp
        })
    # Erstelle gdf aus den Passagier Daten
    passengers_gdf = gpd.GeoDataFrame(passengers)

    # Überprüfe die Validität der Knoten in den Abschnitten
    section_trip_points = validate_nodes_in_data(section_trip_points, main_stop_nodes, passengers_gdf)

    return section_trip_points, successful_trips, passengers_gdf


def calculate_passenger_travel_time(sorted_section_trip_points, graph, passengers_gdf):
    travel_times = []
    flattened_route = [item for sublist in sorted_section_trip_points for item in sublist]

    for index, row in passengers_gdf.iterrows():
        origin = row['origin']
        destination = row['destination']

        # Erstelle die Route für den Passagier
        route = []
        found_origin = False

        for point in flattened_route:
            if point == origin:
                # Falls der Origin Punkt gefunden wird, leere die Route und füge den Origin Punkt hinzu
                route = [point]
                found_origin = True
            elif found_origin:
                route.append(point)
                if point == destination:
                    break

        # Sicherstellen, dass die Route sowohl den Ursprung als auch das Ziel enthält
        if not route or route[0] != origin or route[-1] != destination:
            raise ValueError("Ungültige Route: Zielpunkt kommt vor dem Ursprungspunkt oder Route ist ungültig.")

        # Berechne die Reisezeit entlang der Route
        travel_time = 0
        for i in range(len(route) - 1):
            travel_time += nx.shortest_path_length(graph, route[i], route[i + 1],
                                                   weight='travel_time') / 60  # in Minuten

        # Füge die Reisezeit zum DataFrame hinzu
        travel_times.append(travel_time)

    passengers_gdf['travel_time'] = travel_times

    return passengers_gdf


def split_sections(input_list):
    section1 = input_list[0]
    section2 = input_list[1]
    section3 = input_list[2]
    section4 = input_list[3]

    return section1, section2, section3, section4

def route_node(G, sections):
    routes = []
    for section in sections:
        route = []
        for i in range(len(section) - 1):
            route.extend(nx.shortest_path(G, section[i], section[i + 1], weight='travel_time'))
        routes.append(route)
    return routes


def calculate_section_travel_time(route, graph):
    total_travel_time = 0

    for node in route:
        for i in range(len(node) - 1):
            start_node = node[i]
            end_node = node[i + 1]
            travel_time = nx.shortest_path_length(graph, start_node, end_node, weight='travel_time')
            total_travel_time += travel_time

    return total_travel_time

def passenger_in_vehicle(section, demand_gdf, target_gdf):
    passengers_count = {}
    max_passengers = 0
    current_passengers = 0

    # Initialisierung des Dictionarys mit Nullen für alle Nodes in der Strecke
    for sublist in section:
        for node in sublist:
            passengers_count[node] = 0

    # Durchgehen der section und Inkrementieren/Dekrementieren der Passagieranzahl entsprechend der Fahrgastbewegungen
    for sublist in section:
        for node in sublist:
            if node in demand_gdf['nearest_node'].values:
                current_passengers += 1
                #print('current_passengers', current_passengers)
            elif node in target_gdf['nearest_node'].values:
                current_passengers -= 1
                #print('current_passengers', current_passengers)

            passengers_count[node] = current_passengers
            max_passengers = max(max_passengers, current_passengers)

    return max_passengers

def calculate_route_travel_distance(route, graph):
    total_travel_distance = 0

    for node in route:
        for i in range(len(node) - 1):
            start_node = node[i]
            end_node = node[i + 1]
            travel_distance = nx.shortest_path_length(graph, start_node, end_node, weight='length')
            total_travel_distance += travel_distance

    return total_travel_distance / 1000  # Umrechnung von Metern in Kilometer