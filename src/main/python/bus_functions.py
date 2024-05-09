import pyproj
import pandas as pd
import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt
from shapely.geometry import Point
import osmnx as ox
import json

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
def compute_shortest_paths(G, points_gdf):
    routes = []
    route_lengths = []
    for idx, row in points_gdf.iterrows():
        orig = get_nearest_node(G, row['geometry'])
        next_row = points_gdf.iloc[(idx + 1) % len(points_gdf)]
        dest = get_nearest_node(G, next_row['geometry'])
        route = ox.shortest_path(G, orig, dest, weight="length")
        routes.append(route)
        route_length = sum(ox.utils_graph.get_route_edge_attributes(G, route, "length"))
        route_lengths.append(route_length)
    return routes, route_lengths


def load_geojson(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def passengers_on_bus(bus_stops_gdf, demand_geojson, destination_geojson):
    passengers = []
    bus_stop_coords = [(point.x, point.y) for point in bus_stops_gdf.geometry]

    for demand_feature, dest_feature in zip(demand_geojson['features'], destination_geojson['features']):
        passenger_origin = Point(demand_feature['geometry']['coordinates'])
        passenger_destination = Point(dest_feature['geometry']['coordinates'])

        origin_in_buffer = False
        destination_in_buffer = False
        for coord in bus_stop_coords:
            bus_stop_point = Point(coord)
            if bus_stop_point.buffer(500).contains(passenger_origin):
                origin_in_buffer = True
                start = bus_stop_point
            if bus_stop_point.buffer(500).contains(passenger_destination):
                destination_in_buffer = True
                end = bus_stop_point
            if origin_in_buffer and destination_in_buffer:
                passengers.append({
                    'origin': passenger_origin,
                    'destination': passenger_destination,
                    'start': start,
                    'end': end,
                    'timestamp': demand_feature['properties']['timestamp']
                })
                break

    passengers_gdf = gpd.GeoDataFrame(passengers, geometry='origin')
    return passengers_gdf


def compute_shortest_paths_travel_time(G, passengers_gdf):
    # routes = []
    route_travel_times = []

    for idx, row in passengers_gdf.iterrows():
        orig = get_nearest_node(G, lv95_to_wgs84(row['start']))
        dest = get_nearest_node(G, lv95_to_wgs84(row['end']))

        # Berechne die Reisezeit für den kürzesten Pfad
        route_travel_time = nx.shortest_path_length(G, orig, dest, weight='travel_time')
        route_travel_times.append(route_travel_time)
        print("Reisezeit von", orig, "nach", dest, ":", route_travel_time, "Minuten")

    # Füge die Spalte 'travel_time' mit den berechneten Reisezeiten zum DataFrame hinzu
    passengers_gdf['travel_time'] = route_travel_times

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
    destination_legend = plt.Line2D([], [], color='blue', marker='o', markersize=8, linestyle='None', label='Destination Points')
    passengers_demand_legend = plt.Line2D([], [], color='orange', marker='o', markersize=8, linestyle='None', label='Passengers origin')
    passengers_destination_legend = plt.Line2D([], [], color='yellow', marker='o', markersize=8, linestyle='None', label='Passengers destination')

    ax.legend(handles=[demand_legend, destination_legend, passengers_demand_legend, passengers_destination_legend], loc='upper left')

    plt.show()

def count_passengers(passengers_gdf):
    num_passengers = passengers_gdf.shape[0]
    return num_passengers
    print("Anzahl der Passagiere im Bus:", num_passengers)

# Funktion zum Plotten der Routen auf dem Straßennetzwerk
def plot_routes(G, routes):
    fig, ax = ox.plot_graph_routes(G, routes, node_size=0)
    plt.show()
