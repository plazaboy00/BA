import pyproj
import pandas as pd
import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt
from shapely.geometry import LineString, Point
from shapely.ops import nearest_points
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
            section_points_lists.append([(prev_nearest_node, 2), (current_nearest_node, 3)])
        prev_nearest_node = current_nearest_node

    return section_points_lists


def add_demandnode_to_section(start_node, target_node, demand_node, section_trip_points):
    # Durchlaufe jede Liste in der Liste
    for sublist in section_trip_points:
        # Überprüfe, ob beide Input-Elemente in der aktuellen Unterliste enthalten sind
        if start_node == sublist[0][0] and target_node == sublist[-1][0]:
            # Füge das Tupel (demand_node, 0) zur Unterliste hinzu
            sublist.insert(-1, (demand_node, 0))  # Füge (demand_node, 0) vor target_node ein
            return section_trip_points  # Gib die gesamte Liste zurück, nachdem das Element hinzugefügt wurde
    return section_trip_points  # Falls keine passende Unterliste gefunden wurde, gib die unveränderte Liste zurück


def add_targetnode_to_section(start_node, target_node, demand_node, section_trip_points):
    # Durchlaufe jede Liste in der Liste
    for sublist in section_trip_points:
        # Überprüfe, ob beide Input-Elemente in der aktuellen Unterliste enthalten sind
        if start_node == sublist[0][0] and target_node == sublist[-1][0]:
            # Füge das Tupel (demand_node, 0) zur Unterliste hinzu
            sublist.insert(-1, (demand_node, 1))  # Füge (demand_node, 0) vor target_node ein
            return section_trip_points  # Gib die gesamte Liste zurück, nachdem das Element hinzugefügt wurde
    return section_trip_points  # Falls keine passende Unterliste gefunden wurde, gib die unveränderte Liste zurück


def insert_demand_node_by_shortest_path(sorted_section_trip_points, graph, demand_node):
    sorted_sublists = []

    for sublist in sorted_section_trip_points:
        start_node = sublist[0][0]  # Der erste Wert im ersten Tupel
        end_node = sublist[-1][0]  # Der erste Wert im letzten Tupel

        # Extrahiere die bestehenden Nodes ohne das erste und letzte Element
        existing_nodes = sublist[1:-1]
        sorted_nodes = []
        node_before_demand = (start_node, 2)
        demand_node_reached = False

        for node, nodetype in existing_nodes:
            # Berechne den Abstand von der demand_node zu diesem Knoten
            path_to_next_node = nx.shortest_path_length(graph, node_before_demand[0], node, weight='travel_time')
            path_to_demand_node = nx.shortest_path_length(graph, node_before_demand[0], demand_node, weight='travel_time')

            if path_to_demand_node < path_to_next_node and demand_node_reached == False:
                demand_node_reached = True
                sorted_nodes.append((demand_node, 0))


            # Sortiere die Knoten basierend auf ihrer Entfernung zur demand_node
            sorted_nodes.append((node, nodetype))
            node_before_demand = (node, nodetype)

        # Füge die sortierte Unterliste zur sortierten Liste hinzu, ohne den zweiten Wert der Tupel zu ändern
        sorted_sublist = [sublist[0]] + sorted_nodes + [sublist[-1]]
        sorted_sublists.append(sorted_sublist)

    return sorted_sublists


def sort_sublists_by_shortest_path_with_target(sorted_section_trip_points, graph, demand_node, target_node):
    sorted_sublists = []

    for sublist in sorted_section_trip_points:
        start_node = sublist[0][0]
        end_node = sublist[-1][0]

        # Extrahiere die bestehenden Nodes ohne das erste und letzte Element
        existing_nodes = sublist[1:-1]
        sorted_nodes = []
        demand_node_reached = False
        target_node_inserted = False

        for node, nodetype in existing_nodes:
            if not demand_node_reached:
                sorted_nodes.append((node, nodetype))

            if node == demand_node:
                demand_node_reached = True

            if demand_node_reached and not target_node_inserted:
                path_to_target = nx.shortest_path_length(graph, node, target_node, weight='travel_time')
                path_to_next_node = nx.shortest_path_length(graph, node, target_node, weight='travel_time')

                if path_to_target < path_to_next_node:
                    sorted_nodes.append((target_node, 1))
                    target_node_inserted = True

            if demand_node_reached:
                sorted_nodes.append((node, nodetype))

        # Füge das erste und letzte Element wieder hinzu
        sorted_sublist = [sublist[0]] + sorted_nodes + [sublist[-1]]
        sorted_sublists.append(sorted_sublist)

    return sorted_sublists




def calculate_travel_time_for_updated_section(demand_node, sorted_section_trip_points, graph):
    updated_section_index = None
    travel_time = 30 # Zeit zum Ein-/ Aussteigen

    # Finde den Index der aktualisierten Unterliste, die den demand_node enthält
    for i, sublist in enumerate(sorted_section_trip_points):
        if any(demand_node == node[0] for node in sublist):
            updated_section_index = i
            break

    # Berechne die Reisezeit für die aktualisierte Unterliste
    if updated_section_index is not None:
        for i in range(len(sorted_section_trip_points[updated_section_index]) - 1):
            start_node = sorted_section_trip_points[updated_section_index][i][0]  # Der erste Wert im Tupel
            end_node = sorted_section_trip_points[updated_section_index][i + 1][0]  # Der erste Wert im Tupel
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
        if start_node == sublist[0][0] and target_node == sublist[-1][0] and demand_node in sublist and demand_node != \
                sublist[0][0] and demand_node != sublist[-1][0]:
            # Entferne die demand_node aus der Unterliste
            sublist.remove(demand_node)

    return sorted_section_trip_points

# Hilfsfunktion, um die aktuelle Anzahl der Passagiere im Fahrzeug zu berechnen
def calculate_current_passengers_timon(section_trip_points, demand_node):
    # Gehe durch die section_trip_points bis zum aktuellen demand node
    # Wie viele Passagiere sind im Fahrzeug, wenn der demand node dazugefügt wird?
    current_passengers = 0
    reached = False
    for sublist in section_trip_points:
        for node, action in sublist:
            if reached == True and node != demand_node:
                break
            if action == 0:
                current_passengers += 1
            elif action == 1:
                current_passengers -= 1
            if node == demand_node:
                reached = True
    return current_passengers

# Hilfsfunktion, um die aktuelle Anzahl der Passagiere im Fahrzeug zu berechnen
def calculate_current_passengers(section_trip_points):
    # Gehe durch die section_trip_points durch
    # Überprüfe, ob mit dem neuen demand_node die Anzahl der Passagiere im Fahrzeug überschritten wird
    current_passengers = 0
    max_passengers = 0
    #print(section_trip_points)
    for sublist in section_trip_points:
        for node, action in sublist:
            if action == 0:
                current_passengers += 1
                if current_passengers > max_passengers:
                    max_passengers = current_passengers
            elif action == 1:
                current_passengers -= 1
    return max_passengers


def determine_flag_of_section(section_trip_points, start_node, target_node):
    flag = 0
    for sublist in section_trip_points:
        # Überprüfe, ob beide Input-Elemente in der aktuellen Unterliste enthalten sind
        if start_node == sublist[0][0] and target_node == sublist[-1][0]:
            flag = flag
        else: flag += 1
        return flag

def validate_nodes_in_data(nodes, main_stop_nodes, passengers_gdf):
    validated_nodes = []
    for node_list in nodes:
        section = []
        for node_tuple in node_list:
            node = node_tuple[0]  # Der erste Wert im Tupel
            # Überprüfe, ob der Knoten in den Hauptknoten oder in den Passagieren als Ursprung oder Ziel enthalten ist
            #print(main_stop_nodes)
            #print(passengers_gdf)
            if node in main_stop_nodes['nearest_node'].values or node in passengers_gdf['origin'].values or node in passengers_gdf['destination'].values:
                section.append(node_tuple)  # Füge das gesamte Tupel hinzu
        validated_nodes.append(section)

    return validated_nodes


# Hauptfunktion von odpt
def process_demand_points(demand_nodes, target_nodes, main_stop_nodes, max_travel_time_per_section, start_timestamp, max_capacity, G):
    successful_trips = 0
    #max_capacity = 31
    passengers = []

    section_trip_points = create_section_trip_points(main_stop_nodes)
    #print('section_trip_points erstellt', section_trip_points)
    number_of_sublists = len(section_trip_points)
    sublists_flags = [False] * number_of_sublists
    bus_timestamp = start_timestamp

    # Iteriere über die Nachfrageknoten
    for demand_index, demand_row in demand_nodes.iterrows():
        demand_gemeinde = demand_row['gemeinde']
        demand_node = demand_row['nearest_node']
        demand_start_stop, demand_end_stop = demand_row['section']
        demand_timestamp = demand_row['timestamp']

        # print(demand_timestamp)
        #print('demand node', demand_node)

        # Suche den Start-Hauptknoten des Demand-Knotens
        demand_start_stop_row = main_stop_nodes.loc[main_stop_nodes.index == demand_start_stop]
        nearest_node_demand_start = demand_start_stop_row['nearest_node'].values[0]

        # Suche den Ziel-Hauptknoten des Demand-Knotens
        demand_end_stop_row = main_stop_nodes.loc[main_stop_nodes.index == demand_end_stop]
        nearest_node_demand_end = demand_end_stop_row['nearest_node'].values[0]

        # Überprüfe, ob die Section des demand_nodes voll ist
        if sublists_flags[determine_flag_of_section(section_trip_points, nearest_node_demand_start, nearest_node_demand_end)] == True:
            #print('Section ist voll')
            continue

        # Füge demand_node zu den Abschnitts-Trip-Punkten hinzu
        section_trip_points = add_demandnode_to_section(nearest_node_demand_start, nearest_node_demand_end, demand_node,
                                                        section_trip_points)
        # print('section_trip_points 2', section_trip_points)
        section_trip_points = insert_demand_node_by_shortest_path(section_trip_points, G, demand_node)
        # print('section_trip_points 3', section_trip_points)

        # Überprüfe, ob die Reisezeit pro Abschnitt die maximale Reisezeit pro Abschnitt überschreitet
        travel_time = calculate_travel_time_for_updated_section(demand_node, section_trip_points, G)
        # print(travel_time)
        if travel_time > max_travel_time_per_section:
            section_trip_points = remove_demand_node_from_sublist(nearest_node_demand_start, nearest_node_demand_end,
                                                                  (demand_node, 0), section_trip_points)
            #print('remove')
            #print('section_trip_points 1', section_trip_points)
            continue

        # Überprüfe, ob der demand_node in der vorgegebenen Zeit abgeholt werden kann
        arrival_time = bus_timestamp + timedelta(seconds=travel_time)
        start_buffer = arrival_time - timedelta(minutes=10)
        end_buffer = arrival_time + timedelta(minutes=10)
        if demand_timestamp < start_buffer or demand_timestamp > end_buffer:
            section_trip_points = remove_demand_node_from_sublist(nearest_node_demand_start, nearest_node_demand_end,
                                                                  (demand_node, 0), section_trip_points)
            #print('remove')
            #print('section_trip_points 2', section_trip_points)
            continue

        # Überprüfe, ob das Fahrzeug voll ist
        max_passengers = calculate_current_passengers(section_trip_points)
        #print('max_passengers', max_passengers)
        #print('section_trip_points 1', section_trip_points)
        if max_passengers > max_capacity:
            #print('Fahrzeug ist voll')
            section_trip_points = remove_demand_node_from_sublist(nearest_node_demand_start, nearest_node_demand_end,
                                                                  (demand_node, 0), section_trip_points)

            sublists_flags[determine_flag_of_section(section_trip_points, nearest_node_demand_start,
                                                     nearest_node_demand_end)] = True
            #print('remove')
            #print('section_trip_points 3', section_trip_points)
            continue

        # Finde die zugehörigen Zielknoten für diesen Demand-Knoten
        corresponding_target_node = target_nodes.loc[target_nodes['passagier_nummer'] == demand_row['passagier_nummer']]
        if corresponding_target_node.empty:
            print(f"Kein Zielknoten gefunden für Passagier {demand_row['passagier_nummer']}")
            continue
        section_tuple = corresponding_target_node['section'].values[0]
        target_start_stop, target_end_stop = section_tuple
        target_node = corresponding_target_node['nearest_node'].values[0]
        target_gemeinde = corresponding_target_node['gemeinde'].values[0]

        #print('target_node', target_node)

        # Überprüfe, ob der demand und der target Knoten dieselben sind
        if demand_node == target_node:
            #print('Der Demand- und Zielknoten sind identisch')
            section_trip_points = remove_demand_node_from_sublist(nearest_node_demand_start, nearest_node_demand_end,
                                                                  (demand_node, 0), section_trip_points)
            #print('remove')
            #print('section_trip_points 4', section_trip_points)
            continue

        # Suche den Start-Hauptknoten des Ziel-Knotens
        target_start_stop_row = main_stop_nodes.loc[main_stop_nodes.index == target_start_stop]
        nearest_node_target_start = target_start_stop_row['nearest_node'].values[0]

        # Suche den Ziel-Hauptknoten des Ziel-Knotens
        target_end_stop_row = main_stop_nodes.loc[main_stop_nodes.index == target_end_stop]
        nearest_node_target_end = target_end_stop_row['nearest_node'].values[0]

        section_trip_points = add_targetnode_to_section(nearest_node_target_start, nearest_node_target_end, target_node,
                                                        section_trip_points)
        #print('bevor', section_trip_points)
        section_trip_points = sort_sublists_by_shortest_path_with_target(section_trip_points, G, demand_node, target_node)
        #print('danach', section_trip_points)

        # Überprüfe, ob der target_node in der gleichen section ist wie der demand_node
        if nearest_node_demand_start == nearest_node_target_start and nearest_node_target_end == nearest_node_demand_end:
            # Berechne die Reisezeit für die aktualisierte Unterliste
            travel_time_target = calculate_travel_time_for_updated_section(target_node, section_trip_points, G)
            if travel_time_target > max_travel_time_per_section:
                section_trip_points = remove_demand_node_from_sublist(nearest_node_demand_start,
                                                                      nearest_node_demand_end, (demand_node, 0),
                                                                      section_trip_points)
                section_trip_points = remove_demand_node_from_sublist(nearest_node_target_start,
                                                                      nearest_node_target_end, (target_node, 0),
                                                                      section_trip_points)
                #print('remove')
                #print('section_trip_points 5', section_trip_points)
                continue

        # Überprüfe, ob die Reisezeit pro Abschnitt die maximale Reisezeit pro Abschnitt überschreitet
        travel_time_target = calculate_travel_time_for_updated_section(target_node, section_trip_points, G)
        if travel_time_target > max_travel_time_per_section:
            section_trip_points = remove_demand_node_from_sublist(nearest_node_demand_start, nearest_node_demand_end,
                                                                  (demand_node, 0), section_trip_points)
            section_trip_points = remove_demand_node_from_sublist(nearest_node_target_start, nearest_node_target_end,
                                                                  (target_node, 0), section_trip_points)
            #print('remove')
            #print('section_trip_points 6', section_trip_points)
            continue

        # Setze die Flag zurück
        sublists_flags[determine_flag_of_section(
            section_trip_points, nearest_node_target_start, nearest_node_target_end)] = False
        #print('demand', demand_node)
        #print('target', target_node)
        #print('section_trip_points final', section_trip_points)

        # Die Route zwischen Hauptknoten liegt innerhalb der Zeitbeschränkung
        successful_trips += 1
        passengers.append({
            'origin': demand_node,
            'destination': target_node,
            'id': demand_row['passagier_nummer'] - 1,
            'start gemeinde': demand_gemeinde,
            'end gemeinde': target_gemeinde,
            'timestamp': demand_timestamp
        })
    # Erstelle gdf aus den Passagier Daten
    #print(successful_trips)
    passengers_gdf = gpd.GeoDataFrame(passengers)
    #print('passenger', passengers_gdf)

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

        for node, action in flattened_route:
            if node == origin:
                # Falls der Origin Punkt gefunden wird, leere die Route und füge den Origin Punkt hinzu
                route = [node]
                found_origin = True
            elif found_origin:
                route.append(node)
                if node == destination:
                    break

        # Sicherstellen, dass die Route sowohl den Ursprung als auch das Ziel enthält
        if not route or route[0] != origin or route[-1] != destination:
            print(origin)
            print(destination)
            print(node)
            print(route)
            print(flattened_route)
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


def add_zones_to_gdf(passengers_gdf):
    # Iteriere über die Zeilen des DataFrames
    for index, row in passengers_gdf.iterrows():
        if row['start gemeinde'] == row['end gemeinde']:
            passengers_gdf.at[index, 'zone'] = 1
        elif (row['start gemeinde'] == 'Meilen' and row['end gemeinde'] == 'Uster') or \
                (row['start gemeinde'] == 'Uster' and row['end gemeinde'] == 'Meilen'):
            passengers_gdf.at[index, 'zone'] = 3
        elif row['start gemeinde'] != row['end gemeinde']:
            passengers_gdf.at[index, 'zone'] = 2
    return passengers_gdf


def calculate_income(passengers_gdf):
    # Berechne den Gesamteinnahmen
    income = 0
    for index, row in passengers_gdf.iterrows():
        if row['zone'] == 1:
            passengers_gdf.at[index, 'income'] = 2.80  # CHF
        elif row['zone'] == 2:
            passengers_gdf.at[index, 'income'] = 4.60  # CHF
        elif row['zone'] == 3:
            passengers_gdf.at[index, 'income'] = 7.00  # CHF
    return passengers_gdf


def split_sections(input_list):
    section1 = [item[0] for item in input_list[0]]
    section2 = [item[0] for item in input_list[1]]
    section3 = [item[0] for item in input_list[2]]
    section4 = [item[0] for item in input_list[3]]

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


def calculate_route_travel_distance(route, graph):
    total_travel_distance = 0

    for node in route:
        for i in range(len(node) - 1):
            start_node = node[i]
            end_node = node[i + 1]
            travel_distance = nx.shortest_path_length(graph, start_node, end_node, weight='length')
            total_travel_distance += travel_distance

    return total_travel_distance / 1000  # Umrechnung von Metern in Kilometer


def process_demand_points_repeatedly(demand_nodes, target_nodes, main_stop_nodes, max_travel_time_per_section,
                                     start_timestamp, max_capacity_per_vehicle, G, repetitions):
    all_successful_trips = []
    all_passengers_gdfs = []
    all_section_trip_points = []

    for _ in range(repetitions):
        section_trip_points, successful_trips, passengers_gdf = process_demand_points(
            demand_nodes, target_nodes, main_stop_nodes, max_travel_time_per_section,
            start_timestamp, max_capacity_per_vehicle, G)

        all_successful_trips.append(successful_trips)
        all_passengers_gdfs.append(passengers_gdf)
        all_section_trip_points.append(section_trip_points)

        # Entferne bereits bediente Demand-Nodes aus den Daten
        demand_nodes = remove_serviced_demand_nodes(demand_nodes, passengers_gdf)
        target_nodes = remove_serviced_target_nodes(target_nodes, passengers_gdf)

    return all_section_trip_points, all_successful_trips, all_passengers_gdfs


def remove_serviced_demand_nodes(demand_nodes, passengers_gdf):
    # Entferne bereits bediente Demand-Nodes aus den Daten
    demand_nodes = demand_nodes[~demand_nodes.index.isin(passengers_gdf['id'])]
    return demand_nodes


def remove_serviced_target_nodes(target_nodes, passengers_gdf):
    # Entferne bereits bediente Ziel-Nodes aus den Daten
    target_nodes = target_nodes[~target_nodes.index.isin(passengers_gdf['id'])]
    return target_nodes

def updated_all_passenger_gdf(all_passengers_gdfs, all_section_trip_points, G):
    updated_passengers_gdfs = []
    for passengers_gdf, sorted_section_trip_points in zip(all_passengers_gdfs, all_section_trip_points):
        passengers_gdf = calculate_passenger_travel_time(sorted_section_trip_points, G, passengers_gdf)
        passengers_gdf = add_zones_to_gdf(passengers_gdf)
        passengers_gdf = calculate_income(passengers_gdf)
        updated_passengers_gdfs.append(passengers_gdf)
    return updated_passengers_gdfs

def create_sections_routes_all_passengers(all_section_trip_points, G):
    all_routes = []
    all_total_travel_time = []
    all_total_distance = []
    for sorted_section_trip_points in all_section_trip_points:
        # Unterteile die Nodes in die Sektoren
        section1, section2, section3, section4 = split_sections(sorted_section_trip_points)
        route1 = route_node(G, [section1])
        route2 = route_node(G, [section2])
        route3 = route_node(G, [section3])
        route4 = route_node(G, [section4])

        all_routes.append([route1, route2, route3, route4])

        # Reisezeit der Sektoren & gesamt Reisezeit
        travel_time1 = calculate_section_travel_time(route1, G)
        travel_time2 = calculate_section_travel_time(route2, G)
        travel_time3 = calculate_section_travel_time(route3, G)
        travel_time4 = calculate_section_travel_time(route4, G)

        # Strecke des odpt Fahrzeuges
        travel_distance1 = calculate_route_travel_distance(route1, G)
        travel_distance2 = calculate_route_travel_distance(route2, G)
        travel_distance3 = calculate_route_travel_distance(route3, G)
        travel_distance4 = calculate_route_travel_distance(route4, G)

        total_travel_time = (travel_time1 + travel_time2 + travel_time3 + travel_time4) / 60
        print('Gesamtreisezeit in Minuten:', total_travel_time)
        all_total_travel_time.append(total_travel_time)

        total_distance = travel_distance1 + travel_distance2 + travel_distance3 + travel_distance4
        print('Zurückgelegte Distanz:', total_distance, 'km')
        all_total_distance.append(total_distance)
    return all_routes, all_total_travel_time, all_total_distance

def count_passenger_list(all_successful_trips):
    total_passenger = 0
    for passenger in all_successful_trips:
        total_passenger += passenger
    return total_passenger