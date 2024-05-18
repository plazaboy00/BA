from ODPT_functions import *
from plot import *
from bus_functions import add_zones_to_gdf, calculate_income
from roadmap import load_roadmap


def odpt():
    ROOT_FILES = 'C:/Users/Linus/PycharmProjects/BA/'
    ROOT_Busstations = 'src/main/resources/Buslinie/Busstationen/'
    ROOT_odpt_stops = 'src/main/resources/ODPT/'
    ROOT_RESOURCE_STRASSENNETZ = 'src/main/resources/QGIS/Strassen/'

    # Strassennetzwerk aus Roadmap laden
    # G = load_roadmap()
    north, south, east, west = 47.3876, 47.2521, 8.754, 8.6003

    # Herunterladen des Straßennetzwerks basierend auf dem Rechteck
    G = ox.graph.graph_from_bbox(north, south, east, west, network_type='drive')

    # Konvertieren des Graphen in ein GeoJSON-FeatureCollection
    features = ox.graph_to_gdfs(G, nodes=False, edges=True)
    geojson_data = features.to_json()

    # Bestimmen des relativen Pfads
    file_path = ROOT_FILES + ROOT_RESOURCE_STRASSENNETZ + "strassenetzwerk.geojson"

    # Schreiben den GeoJSON-Daten in die Datei
    with open(file_path, "w") as f:
        json.dump(geojson_data, f)

    # impute edge (driving) speeds and calculate edge travel times
    G = ox.speed.add_edge_speeds(G)
    G = ox.speed.add_edge_travel_times(G)

    # you can convert MultiDiGraph to/from GeoPandas GeoDataFrames
    # print(type(G))
    gdf_nodes, gdf_edges = ox.utils_graph.graph_to_gdfs(G)
    G = ox.utils_graph.graph_from_gdfs(gdf_nodes, gdf_edges, graph_attrs=G.graph)

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

    # Funktion preprocess_gdfs
    demand_gdf, target_gdf, main_stops_gdf, odpt_stops_wgs84_gdf = \
        preprocess_gdfs(demand_gdf_wgs84, target_gdf_wgs84,
                        odpt_stops_with_return_wgs84, odpt_stops_wgs84, G)

    # Sortiere, die Nachfrage punkte nach ihrer Effizienz / Entfernung
    sorted_demand_gdf, sorted_target_gdf = sort_demand_target_nodes \
        (G, demand_gdf, target_gdf, main_stops_gdf)

    # Füge die section zu den Nachfrage- und Ziel Punkten dazu
    demand_gdf, target_gdf = add_section_to_points(G, sorted_demand_gdf, sorted_target_gdf, odpt_stops_wgs84)
    # Sortiere die Target-Nodes in die section nach dem Demand-Node
    demand_gdf, target_gdf = sort_target_section(demand_gdf, target_gdf)

    # Annahme setze die maximale Reisezeit pro Abschnitt auf 15 Minuten
    max_travel_time_per_section = 900  # 15 Minuten
    start_timestamp = pd.Timestamp('2018-04-20 09:05:00')
    sorted_section_trip_points, successful_trips, passengers_gdf = process_demand_points\
        (demand_gdf, target_gdf, main_stops_gdf, max_travel_time_per_section, start_timestamp, G)
    print(sorted_section_trip_points)
    print('Erfolgreiche Trips:', successful_trips)

    # Berechne die travel time der Passagiere, deren Zonen und die Einnahmen
    passengers_gdf = calculate_passenger_travel_time(sorted_section_trip_points, G, passengers_gdf)
    passengers_gdf = add_zones_to_gdf(passengers_gdf)
    passengers_gdf = calculate_income(passengers_gdf)
    print(passengers_gdf)

    # Unterteile die Nodes in die Sektoren
    section1, section2, section3, section4 = split_sections(sorted_section_trip_points)
    route1 = route_node(G, [section1])
    route2 = route_node(G, [section2])
    route3 = route_node(G, [section3])
    route4 = route_node(G, [section4])

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

    max_passengers = passenger_in_vehicle(sorted_section_trip_points, demand_gdf, target_gdf)
    print('Höchste Anzahl an Passagieren:', max_passengers)

    total_distance = travel_distance1 + travel_distance2 + travel_distance3 + travel_distance4
    print('Zurückgelegte Distanz:', total_distance, 'km')

    return max_passengers, total_distance, total_travel_time, passengers_gdf


#odpt_passengers, odpt_km, odpt_total_travel_time, passenger_gdf = odpt()
