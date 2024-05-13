import osmnx as ox
from bus_functions import load_street_network, save_street_network
import json


def load_roadmap():
    ROOT_FILES = 'C:/Users/Linus/PycharmProjects/BA/'
    # Pfad zur Shapefile-Datei mit den Strassen
    ROOT_RESOURCE_STRASSENNETZ = 'src/main/resources/QGIS/Strassen/'

    # Definieren des Bereichs für das Straßennetzwerk
    north, south, east, west = 47.3667, 47.2586, 8.754, 8.6103

    # Laden des Straßennetzwerks
    graph = load_street_network(north, south, east, west)

    # Konvertieren des Graphen in ein GeoJSON-FeatureCollection
    features = ox.graph_to_gdfs(graph, nodes=False, edges=True)
    geojson_data = features.to_json()

    # Bestimmen des relativen Pfads
    file_path = ROOT_FILES + ROOT_RESOURCE_STRASSENNETZ + "strassenetzwerk.geojson"

    # Schreiben den GeoJSON-Daten in die Datei
    with open(file_path, "w") as f:
        json.dump(geojson_data, f)

    # impute edge (driving) speeds and calculate edge travel times
    graph = ox.speed.add_edge_speeds(graph)
    graph = ox.speed.add_edge_travel_times(graph)

    # you can convert MultiDiGraph to/from GeoPandas GeoDataFrames
    gdf_nodes, gdf_edges = ox.utils_graph.graph_to_gdfs(graph)
    graph = ox.utils_graph.graph_from_gdfs(gdf_nodes, gdf_edges, graph_attrs=graph.graph)
    # Speichern des Straßennetzwerks als GeoPackage
    save_street_network(graph, ROOT_FILES + ROOT_RESOURCE_STRASSENNETZ + "OSMStrassennetz.gpkg")

    return graph
