import geopandas as gpd
from shapely.geometry import LineString

ROOT_FILES = 'C:/Users/Linus/PycharmProjects/BA/'
ROOT_Busstations = 'src/main/resources/Buslinie/Busstationen/'
class BusLine:
    def __init__(self, name):
        self.name = name
        self.stops = []

    def add_stop(self, stop_name, latitude, longitude):
        stop = {
            "name": stop_name,
            "latitude": latitude,
            "longitude": longitude
        }
        self.stops.append(stop)

    def get_stops(self):
        return self.stops

    def print_stops(self):
        for i, stop in enumerate(self.stops, start=1):
            print(f"{i}. {stop['name']} (Lat: {stop['latitude']}, Lon: {stop['longitude']})")



# Pfad zur Shapefile-Datei mit den Bushaltestellen
shapefile_path = ROOT_FILES + ROOT_Busstations + "pfad/zur/deiner/Stationspuffer.shp"

# Laden der Bushaltestellen als GeoDataFrame
bus_stops = gpd.read_file(shapefile_path)

# Erstellen einer Linie, die die Bushaltestellen verbindet
bus_line = LineString(bus_stops.geometry)

# Konvertieren der Linie in ein GeoDataFrame
bus_line_gdf = gpd.GeoDataFrame(geometry=[bus_line])

# Speichern der Linie als Shapefile oder in einem anderen gewünschten Format
output_path = "pfad/zum/ausgabedatei.shp"
bus_line_gdf.to_file(output_path)



# Beispiel einer Buslinie erstellen
bus_line = BusLine("Bus 123")

# Haltestellen hinzufügen
bus_line.add_stop("Haltestelle A", 52.5200, 13.4050)
bus_line.add_stop("Haltestelle B", 52.5233, 13.4115)
bus_line.add_stop("Haltestelle C", 52.5250, 13.4150)

# Liste der Haltestellen abrufen und ausgeben
stops = bus_line.get_stops()
print("Liste der Haltestellen:")
bus_line.print_stops()
