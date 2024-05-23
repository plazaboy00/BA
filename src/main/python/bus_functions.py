import pyproj
import pandas as pd
import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt
from shapely.geometry import Point
import osmnx as ox
import json
from datetime import datetime, timedelta

# Projektionsdefinitionen
lv95 = pyproj.Proj(init='epsg:2056')
wgs84 = pyproj.Proj(init='epsg:4326')


# Funktion zur Konvertierung von LV95 nach WGS84
def lv95_to_wgs84(point):
    x_lv95, y_lv95 = point.x, point.y
    x_wgs84, y_wgs84 = pyproj.transform(lv95, wgs84, x_lv95, y_lv95)
    return Point(x_wgs84, y_wgs84)


# Funktion zum Laden des Straßennetzwerks
def load_street_network(north, south, east, west):
    return ox.graph.graph_from_bbox(north, south, east, west, network_type='drive')


# Funktion zum Speichern des Straßennetzwerks als GeoPackage
def save_street_network(G, filepath):
    ox.io.save_graph_geopackage(G, filepath)


# Funktion zum Hinzufügen der Rückfahrt-Haltestellen
def add_return_trip(bus_stops):
    return_trip_stops = bus_stops.iloc[:-1].iloc[::-1]
    return pd.concat([bus_stops, return_trip_stops], ignore_index=True)


# Funktion zur Bestimmung des nächsten Netzwerkknotens zu einem Punkt
def get_nearest_node(G, point):
    return ox.distance.nearest_nodes(G, point.x, point.y)


# Funktion zum Berechnen des kürzesten Pfads zwischen den Haltestellen
def compute_shortest_paths(G, points_gdf, start_time, waiting_time):
    routes = []
    route_lengths = []
    ankunftszeiten = []

    # Startzeit als datetime-Objekt parsen
    aktuelle_zeit = start_time
    ankunftszeiten.append(aktuelle_zeit)
    v = 14  # Geschwindigkeit in m/s

    for idx, row in points_gdf.iterrows():
        orig = get_nearest_node(G, row['geometry'])
        next_idx = (idx + 1) % len(points_gdf)
        next_row = points_gdf.iloc[next_idx]
        dest = get_nearest_node(G, next_row['geometry'])

        # Berechne die Fahrzeit für die aktuelle Route
        route = ox.shortest_path(G, orig, dest, weight="length")
        routes.append(route)
        route_length = sum(ox.utils_graph.get_route_edge_attributes(G, route, "length"))
        route_lengths.append(route_length)

        # Berechne die Reisezeit in Sekunden
        route_travel_time = route_length / v
        aktuelle_zeit += timedelta(seconds=route_travel_time) + timedelta(seconds=waiting_time)
        ankunftszeiten.append(aktuelle_zeit)

        # Füge eine 10-minütige Pause in der Hälfte der Stopps ein
        if (idx + 1) % (len(points_gdf) // 2) == 0:
            aktuelle_zeit += timedelta(minutes=5)

    # Füge die Ankunftszeiten als neue Spalte zur GeoDataFrame hinzu
    points_gdf['ankunftszeit'] = ankunftszeiten[:-1]  # Letzte Zeit ist für den nächsten Startpunkt

    return routes, route_lengths, points_gdf


def load_geojson(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data


def compute_travel_time(passengers_gdf):
    travel_times = []
    for idx, row in passengers_gdf.iterrows():
        start = pd.to_datetime(row['stoptime start'])
        end = pd.to_datetime(row['stoptime end'])
        travel_time = (end - start).total_seconds() / 60  # Convert to minutes
        travel_times.append(travel_time)

    passengers_gdf['travel_time'] = travel_times
    return passengers_gdf


def passengers_on_bus(bus_stops_gdf, demand_geojson, destination_geojson, max_capacity):
    passengers = []
    passenger_number = 0
    max_capacity = 31
    bus_stop_coords = [(point.x, point.y) for point in bus_stops_gdf.geometry]
    bus_stop_times = list(bus_stops_gdf['ankunftszeit'])

    for demand_feature, dest_feature in zip(demand_geojson['features'], destination_geojson['features']):
        if passenger_number == max_capacity:
            print('Fahrzeug ist voll')
            break
        passenger_origin = Point(demand_feature['geometry']['coordinates'])
        start_gemeinde = demand_feature['properties']['gemeinde']
        passenger_destination = Point(dest_feature['geometry']['coordinates'])
        end_gemeinde = dest_feature['properties']['gemeinde']
        passenger_time = datetime.strptime(demand_feature['properties']['timestamp'], '%Y-%m-%dT%H:%M:%S')

        origin_in_buffer = False
        destination_in_buffer = False
        start = None
        end = None
        start_time = None
        end_time = None

        for coord, stop_time in zip(bus_stop_coords, bus_stop_times):
            bus_stop_point = Point(coord)
            start_buffer = stop_time - timedelta(minutes=10)
            end_buffer = stop_time + timedelta(minutes=10)

            if bus_stop_point.buffer(500).contains(passenger_origin) and start_buffer <= passenger_time <= end_buffer:
                origin_in_buffer = True
                start = bus_stop_point
                start_time = stop_time

            if bus_stop_point.buffer(500).contains(passenger_destination) and start_buffer <= passenger_time <= end_buffer:
                destination_in_buffer = True
                end = bus_stop_point
                end_time = stop_time

            # Überprüfen, ob die Start- und Endpunkte unterschiedliche Bushaltestellen sind und die Startzeit vor der Endzeit liegt
            if origin_in_buffer and destination_in_buffer and start != end and start_time < end_time:
                passenger_number += 1
                passengers.append({
                    'origin': passenger_origin,
                    'start gemeinde': start_gemeinde,
                    'destination': passenger_destination,
                    'end gemeinde': end_gemeinde,
                    'start': start,
                    'end': end,
                    'stoptime start': start_time,
                    'stoptime end': end_time,
                    'timestamp': passenger_time
                })
                break

    passengers_gdf = gpd.GeoDataFrame(passengers, geometry='origin')
    return passengers_gdf



def compute_travel_time_bus(busstops_with_time):
    # Konvertieren der 'ankunftszeit'-Spalte in datetime-Objekte
    busstops_with_time['ankunftszeit'] = pd.to_datetime(busstops_with_time['ankunftszeit'])

    # Zugriff auf den ersten und letzten Eintrag der 'ankunftszeit'-Spalte
    first_timestamp = busstops_with_time['ankunftszeit'].iloc[0]
    last_timestamp = busstops_with_time['ankunftszeit'].iloc[-1]

    # Berechnung der Reisezeit
    travel_time = last_timestamp - first_timestamp

    # Konvertieren der Reisezeit in Minuten
    travel_time_minutes = travel_time.total_seconds() / 60

    return travel_time_minutes


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
            passengers_gdf.at[index, 'income'] = 2.80 # CHF
        elif row['zone'] == 2:
            passengers_gdf.at[index, 'income'] = 4.60 # CHF
        elif row['zone'] == 3:
            passengers_gdf.at[index, 'income'] = 7.00 # CHF
    return passengers_gdf


def plot_passengers(passengers_gdf, bus_stops_gdf, demand_geojson, destination_geojson, gemeindegrenzen):
    fig, ax = plt.subplots(figsize=(10, 8))

    bus_stops_gdf.plot(ax=ax, color='grey', markersize=30, label='Bus Stops')

    for feature in demand_geojson['features']:
        point = Point(feature['geometry']['coordinates'])
        ax.plot(point.x, point.y, 'go', markersize=6)

    for feature in destination_geojson['features']:
        point = Point(feature['geometry']['coordinates'])
        ax.plot(point.x, point.y, 'bo', markersize=6)

    origin_gdf = passengers_gdf[['origin', 'timestamp']].copy()
    destination_gdf = gpd.GeoDataFrame()
    destination_gdf['destination'] = None
    destination_gdf['geometry'] = passengers_gdf['destination'].apply(Point)
    destination_gdf = gpd.GeoDataFrame(destination_gdf)
    destination_gdf.set_geometry('geometry', inplace=True)

    origin_gdf.plot(ax=ax, color='orange', markersize=20, label='Origin Points', zorder=2)
    destination_gdf.plot(ax=ax, color='yellow', markersize=20, label='Destination Points', zorder=2)

    gemeindegrenzen.plot(ax=ax, color='black', alpha=0.5, label='Shapefile')

    ax.set_title('Bus Stops, Demand and Destination Points, and Passengers')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')

    demand_legend = plt.Line2D([], [], color='green', marker='o', markersize=8, linestyle='None', label='Demand Points')
    destination_legend = plt.Line2D([], [], color='blue', marker='o', markersize=8, linestyle='None',
                                    label='Destination Points')
    passengers_demand_legend = plt.Line2D([], [], color='orange', marker='o', markersize=8, linestyle='None',
                                          label='Passengers origin')
    passengers_destination_legend = plt.Line2D([], [], color='yellow', marker='o', markersize=8, linestyle='None',
                                               label='Passengers destination')

    ax.legend(handles=[demand_legend, destination_legend, passengers_demand_legend, passengers_destination_legend],
              loc='upper left')

    plt.show()


def count_passengers(passengers_gdf):
    num_passengers = passengers_gdf.shape[0]
    return num_passengers
    print("Anzahl der Passagiere im Bus:", num_passengers)


# Funktion zum Plotten der Routen auf dem Straßennetzwerk
def plot_routes(G, routes):
    fig, ax = ox.plot_graph_routes(G, routes, node_size=0)
    plt.show()
