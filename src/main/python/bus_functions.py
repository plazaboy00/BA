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

# Funktion zum Plotten der Routen auf dem Straßennetzwerk
def plot_routes(G, routes):
    fig, ax = ox.plot_graph_routes(G, routes, node_size=0)
    plt.show()
