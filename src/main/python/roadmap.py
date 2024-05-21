import osmnx as ox
from bus_functions import load_street_network, save_street_network
import json
import os


def load_roadmap():
    # Definiere den Pfad zum Speichern der GeoJSON-Daten
    ROOT_FILES = "C:/Users/Linus/PycharmProjects/BA/"  # Passe dies an deinen Basis-Pfad an
    ROOT_RESOURCE_STRASSENNETZ = "src/main/resources/strassennetz/"
    # file_path = os.path.join(ROOT_FILES, ROOT_RESOURCE_STRASSENNETZ, "strassenetzwerk.geojson")

    # Definiere die Grenzen für das herunterzuladende Straßennetzwerk
    north, south, east, west = 47.3876, 47.2521, 8.754, 8.6003

    # Lade das Straßennetzwerk basierend auf dem Rechteck herunter
    G = ox.graph.graph_from_bbox(north, south, east, west, network_type='drive')

    # Konvertiere den Graphen in ein GeoJSON-FeatureCollection
    gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)
    features = gdf_edges


    # Erstelle das Verzeichnis, falls es nicht existiert
    # os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Speichere die GeoJSON-Daten in eine Datei
    # features.to_file(file_path, driver='GeoJSON')

    # Impute edge (driving) speeds and calculate edge travel times
    G = ox.speed.add_edge_speeds(G)
    G = ox.speed.add_edge_travel_times(G)

    # Konvertiere den Graphen in GeoDataFrames
    gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)

    # Erstelle den Graphen erneut aus den GeoDataFrames
    G = ox.graph_from_gdfs(gdf_nodes, gdf_edges, graph_attrs=G.graph)

    # Speichere den Graphen in eine GraphML-Datei für zukünftige Nutzung
    graphml_file_path = os.path.join(ROOT_FILES, ROOT_RESOURCE_STRASSENNETZ, "strassenetzwerk.graphml")
    ox.save_graphml(G, graphml_file_path)

    # Zum Laden des Graphen in Zukunft:
    G = ox.load_graphml(graphml_file_path)
    return G
