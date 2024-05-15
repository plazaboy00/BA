import numpy as np
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

ROOT_FILES = 'C:/Users/Linus/PycharmProjects/BA/'
ROOT_RESOURCE = 'src/main/resources/QGIS/Nutzungsplan/'

def create_geo_dataframe(geo_files):
    result = []
    for geo_file in geo_files:
        shapefile_path = ROOT_FILES + ROOT_RESOURCE + geo_file
        frame = gpd.read_file(shapefile_path)
        if not frame.empty:  # Prüft, ob das GeoDataFrame nicht leer ist
            result.append(frame)

    if result:
        gdf = gpd.GeoDataFrame(pd.concat(result, ignore_index=True))
    else:
        gdf = gpd.GeoDataFrame()  # Wenn keine Daten vorhanden sind, wird ein leeres GeoDataFrame erstellt

    return gdf


def filter_data(daten, gewuenschtes_jahr, gewuenschte_gemeinden,
                gewuenschte_zielnamen, gewuenschte_kategorien,
                gewuenschte_verkehrsmittel):
    return daten[(daten['jahr'] == gewuenschtes_jahr) &
                 (daten['quelle_name'].isin(gewuenschte_gemeinden)) &
                 (daten['ziel_name'].isin(gewuenschte_zielnamen)) &
                 (daten['kategorie'].isin(gewuenschte_kategorien)) &
                 (daten['verkehrsmittel'].isin(gewuenschte_verkehrsmittel))]

def filter_target_data(daten_filtered, target):
    return daten_filtered[(daten_filtered['quelle_name'] == target)
                          & (daten_filtered['quelle_name']
                             != daten_filtered['ziel_name'])]

def filter_and_calculate_traffic_data(data, gemeinde_quelle, gemeinde_ziel, verkehrsmittel, jahr, kategorie):
    filtered_data = data[
        (data['quelle_name'] == gemeinde_quelle) &
        (data['ziel_name'] == gemeinde_ziel) &
        (data['verkehrsmittel'] == verkehrsmittel) &
        (data['jahr'] == jahr) &
        (data['kategorie'] == kategorie)
    ]
    return filtered_data['wert'].values[0]

def berechne_verkehrsaufkommen(gemeinde_oev, gemeinde_miv, modal_split_miv):
    gesamt_verkehrsaufkommen = gemeinde_oev + gemeinde_miv
    neues_verkehrsaufkommen_oev = gesamt_verkehrsaufkommen * (modal_split_miv / 100)
    return neues_verkehrsaufkommen_oev

def calculate_demand(daten, stunden_verkehrstag, prozent_verteilung_hoch,
                     prozent_verteilung_mittel, prozent_verteilung_niedrig):
    nachfrage = int(daten['wert'].sum() / stunden_verkehrstag)
    #nachfrage_zentral = int(prozent_verteilung_hoch * nachfrage)
    nachfrage_höhere_Dichte = int(prozent_verteilung_mittel * nachfrage)
    nachfrage_niedrige_Dichte = int(prozent_verteilung_niedrig * nachfrage)
    nachfrage_zentral = nachfrage - nachfrage_höhere_Dichte - nachfrage_niedrige_Dichte
    return nachfrage, nachfrage_zentral,\
        nachfrage_höhere_Dichte, nachfrage_niedrige_Dichte

def calculate_new_demand(daten, additional_data, stunden_verkehrstag, prozent_verteilung_hoch,
                     prozent_verteilung_mittel, prozent_verteilung_niedrig):
    nachfrage = int((daten['wert'].sum() + additional_data) / stunden_verkehrstag)
    #nachfrage_zentral = int(prozent_verteilung_hoch * nachfrage)
    nachfrage_höhere_Dichte = int(prozent_verteilung_mittel * nachfrage)
    nachfrage_niedrige_Dichte = int(prozent_verteilung_niedrig * nachfrage)
    nachfrage_zentral = nachfrage - nachfrage_höhere_Dichte - nachfrage_niedrige_Dichte
    return nachfrage, nachfrage_zentral,\
        nachfrage_höhere_Dichte, nachfrage_niedrige_Dichte

def generate_random_timestamp(start, end, n):
    time_diff = (end - start).total_seconds()
    random_seconds = np.random.randint(0, int(time_diff), n)
    return [start + pd.Timedelta(seconds=sec) for sec in random_seconds]
def verteile_nachfragepunkte(gemeinde, nachfrage_zentral, nachfrage_höhere_Dichte,
                             nachfrage_niedrige_Dichte, gemeinden_zentral_gdfs,
                             gemeinden_höhere_Dichte_gdfs, gemeinden_niedrige_Dichte_gdfs,
                             start_timestamp, end_timestamp):
    nachfragepunkte_zentral = np.random.choice(
        gemeinden_zentral_gdfs[gemeinden_zentral_gdfs['GEMEINDE'] == gemeinde].index,
        size=nachfrage_zentral)
    nachfragepunkte_höhere_Dichte = np.random.choice(
        gemeinden_höhere_Dichte_gdfs[gemeinden_höhere_Dichte_gdfs['GEMEINDE']
                                     == gemeinde].index, size=nachfrage_höhere_Dichte)
    nachfragepunkte_niedrige_Dichte = np.random.choice(
        gemeinden_niedrige_Dichte_gdfs[gemeinden_niedrige_Dichte_gdfs['GEMEINDE']
                                       == gemeinde].index, size=nachfrage_niedrige_Dichte)

    # Generiere Zeitstempel für die Nachfragepunkte
    nachfragepunkte_zentral_timestamps = generate_random_timestamp(start_timestamp, end_timestamp, nachfrage_zentral)
    nachfragepunkte_höhere_Dichte_timestamps = generate_random_timestamp(start_timestamp, end_timestamp, nachfrage_höhere_Dichte)
    nachfragepunkte_niedrige_Dichte_timestamps = generate_random_timestamp(start_timestamp, end_timestamp, nachfrage_niedrige_Dichte)

    return (nachfragepunkte_zentral, nachfragepunkte_zentral_timestamps), \
           (nachfragepunkte_höhere_Dichte, nachfragepunkte_höhere_Dichte_timestamps), \
           (nachfragepunkte_niedrige_Dichte, nachfragepunkte_niedrige_Dichte_timestamps)

def prepare_demand_data(gemeinden_zentral_gdfs, gemeinden_höhere_Dichte_gdfs, gemeinden_niedrige_Dichte_gdfs,
                        nachfrage_zentral, nachfrage_höhere_Dichte, nachfrage_niedrige_Dichte,
                        nachfrage_zentral_timestamps, nachfrage_höhere_Dichte_timestamps,
                        nachfrage_niedrige_Dichte_timestamps, Gemeinde):

    # Plotten der Nachfragepunkte für Meilen
    punkte_zentral = gemeinden_zentral_gdfs.loc[nachfrage_zentral, 'geometry'].centroid
    punkte_höhere_Dichte = gemeinden_höhere_Dichte_gdfs.loc[nachfrage_höhere_Dichte, 'geometry'].centroid
    punkte_niedrige_Dichte = gemeinden_niedrige_Dichte_gdfs.loc[nachfrage_niedrige_Dichte, 'geometry'].centroid

    # Erstellen eines GeoDataFrame für die Punkte von Meilen mit Zeitstempel
    punkte_zentral_gdf = gpd.GeoDataFrame(geometry=punkte_zentral, crs=gemeinden_zentral_gdfs.crs)
    punkte_zentral_gdf['timestamp'] = nachfrage_zentral_timestamps
    punkte_zentral_gdf['gemeinde'] = Gemeinde
    punkte_höhere_Dichte_gdf = gpd.GeoDataFrame(geometry=punkte_höhere_Dichte, crs=gemeinden_höhere_Dichte_gdfs.crs)
    punkte_höhere_Dichte_gdf['timestamp'] = nachfrage_höhere_Dichte_timestamps
    punkte_höhere_Dichte_gdf['gemeinde'] = Gemeinde
    punkte_niedrige_Dichte_gdf = gpd.GeoDataFrame(geometry=punkte_niedrige_Dichte, crs=gemeinden_niedrige_Dichte_gdfs.crs)
    punkte_niedrige_Dichte_gdf['timestamp'] = nachfrage_niedrige_Dichte_timestamps
    punkte_niedrige_Dichte_gdf['gemeinde'] = Gemeinde

    # Alle Punkte zusammenführen
    alle_punkte_gemeinde = pd.concat([punkte_zentral_gdf, punkte_höhere_Dichte_gdf, punkte_niedrige_Dichte_gdf])


    return alle_punkte_gemeinde

def calculate_demand_bahnhof(daten, daten_bahnhof, stunden_verkehrstag, prozent_verteilung_hoch,
                     prozent_verteilung_mittel, prozent_verteilung_niedrig):
    nachfrage = int(daten['wert'].sum() / stunden_verkehrstag)
    nachfrage_bahnhof = int(((daten_bahnhof['wert'].sum()) / stunden_verkehrstag) / 2)
    nachfrage_gemeinde = nachfrage + nachfrage_bahnhof
    #nachfrage_zentral = int(prozent_verteilung_hoch * nachfrage)
    nachfrage_höhere_Dichte = int(prozent_verteilung_mittel * nachfrage_gemeinde)
    nachfrage_niedrige_Dichte = int(prozent_verteilung_niedrig * nachfrage_gemeinde)
    nachfrage_zentral = nachfrage_gemeinde - nachfrage_höhere_Dichte - nachfrage_niedrige_Dichte
    return nachfrage_gemeinde, nachfrage_bahnhof, nachfrage_zentral,\
        nachfrage_höhere_Dichte, nachfrage_niedrige_Dichte

def verteile_nachfragepunkte_bahnhof(gemeinde, nachfrage_zentral, nachfrage_höhere_Dichte,
                             nachfrage_niedrige_Dichte, nachfrage_bahnhof, gemeinden_zentral_gdfs,
                             gemeinden_höhere_Dichte_gdfs, gemeinden_niedrige_Dichte_gdfs,
                             start_timestamp, end_timestamp):
    nachfragepunkte_zentral = np.random.choice(
        gemeinden_zentral_gdfs[gemeinden_zentral_gdfs['GEMEINDE'] == gemeinde].index,
        size=nachfrage_zentral)
    nachfragepunkte_höhere_Dichte = np.random.choice(
        gemeinden_höhere_Dichte_gdfs[gemeinden_höhere_Dichte_gdfs['GEMEINDE']
                                     == gemeinde].index, size=nachfrage_höhere_Dichte)
    nachfragepunkte_niedrige_Dichte = np.random.choice(
        gemeinden_niedrige_Dichte_gdfs[gemeinden_niedrige_Dichte_gdfs['GEMEINDE']
                                       == gemeinde].index, size=nachfrage_niedrige_Dichte)

    # Generiere Zeitstempel für die Nachfragepunkte
    nachfragepunkte_zentral_timestamps = generate_random_timestamp(start_timestamp, end_timestamp, nachfrage_zentral)
    nachfragepunkte_höhere_Dichte_timestamps = generate_random_timestamp(start_timestamp, end_timestamp, nachfrage_höhere_Dichte)
    nachfragepunkte_niedrige_Dichte_timestamps = generate_random_timestamp(start_timestamp, end_timestamp, nachfrage_niedrige_Dichte)
    nachfragepunkte_bahnhof_timestamps = generate_random_timestamp(start_timestamp, end_timestamp, nachfrage_bahnhof)

    return (nachfragepunkte_zentral, nachfragepunkte_zentral_timestamps), \
           (nachfragepunkte_höhere_Dichte, nachfragepunkte_höhere_Dichte_timestamps), \
           (nachfragepunkte_niedrige_Dichte, nachfragepunkte_niedrige_Dichte_timestamps), \
           nachfragepunkte_bahnhof_timestamps

def prepare_demand_data_bahnhof(gemeinden_zentral_gdfs, gemeinden_höhere_Dichte_gdfs, gemeinden_niedrige_Dichte_gdfs,
                        nachfrage_zentral, nachfrage_höhere_Dichte, nachfrage_niedrige_Dichte,
                        nachfrage_zentral_timestamps, nachfrage_höhere_Dichte_timestamps,
                        nachfrage_niedrige_Dichte_timestamps, Gemeinde, bahnhof_gdf, nachfrage_bahnhof_timestamps):

    # Plotten der Nachfragepunkte für Meilen
    punkte_zentral = gemeinden_zentral_gdfs.loc[nachfrage_zentral, 'geometry'].centroid
    punkte_höhere_Dichte = gemeinden_höhere_Dichte_gdfs.loc[nachfrage_höhere_Dichte, 'geometry'].centroid
    punkte_niedrige_Dichte = gemeinden_niedrige_Dichte_gdfs.loc[nachfrage_niedrige_Dichte, 'geometry'].centroid

    # Erstellen eines GeoDataFrame für die Punkte von Meilen mit Zeitstempel
    punkte_zentral_gdf = gpd.GeoDataFrame(geometry=punkte_zentral, crs=gemeinden_zentral_gdfs.crs)
    punkte_zentral_gdf['timestamp'] = nachfrage_zentral_timestamps
    punkte_zentral_gdf['gemeinde'] = Gemeinde
    punkte_höhere_Dichte_gdf = gpd.GeoDataFrame(geometry=punkte_höhere_Dichte, crs=gemeinden_höhere_Dichte_gdfs.crs)
    punkte_höhere_Dichte_gdf['timestamp'] = nachfrage_höhere_Dichte_timestamps
    punkte_höhere_Dichte_gdf['gemeinde'] = Gemeinde
    punkte_niedrige_Dichte_gdf = gpd.GeoDataFrame(geometry=punkte_niedrige_Dichte, crs=gemeinden_niedrige_Dichte_gdfs.crs)
    punkte_niedrige_Dichte_gdf['timestamp'] = nachfrage_niedrige_Dichte_timestamps
    punkte_niedrige_Dichte_gdf['gemeinde'] = Gemeinde

    # Extrahieren der Geometrie basierend auf dem Namen
    geometry = bahnhof_gdf.loc[bahnhof_gdf['name'] == Gemeinde, 'geometry'].values[0]

    # Erstellen eines neuen DataFrame mit den Timestamps und der extrahierten Geometrie
    punkte_bahnhof = pd.DataFrame({
        'timestamp': nachfrage_bahnhof_timestamps,
        'geometry': [geometry] * len(nachfrage_bahnhof_timestamps)
    })
    punkte_bahnhof_gdf = gpd.GeoDataFrame(punkte_bahnhof, geometry='geometry', crs=bahnhof_gdf.crs)
    punkte_bahnhof_gdf['timestamp'] = nachfrage_bahnhof_timestamps
    punkte_bahnhof_gdf['gemeinde'] = Gemeinde

    # Alle Punkte zusammenführen
    alle_punkte_gemeinde = pd.concat([punkte_zentral_gdf, punkte_höhere_Dichte_gdf, punkte_niedrige_Dichte_gdf, punkte_bahnhof_gdf])

    return alle_punkte_gemeinde

def add_passenger_numbers(gdf):
    gdf['passagier_nummer'] = range(1, len(gdf) + 1)
    return gdf
def xadd_destination_columns(input_gdf, gemeinden_zentral_gdfs, gemeinden_höhere_Dichte_gdfs,
                            gemeinden_niedrige_Dichte_gdfs):
    # Extrahiere die eindeutigen Gemeinden aus dem GeoDataFrame
    gemeinden = input_gdf['gemeinde'].unique()

    # Erstelle ein leeres DataFrame, um die neuen Zeilen hinzuzufügen
    new_rows = []

    # Iteriere über jede Gemeinde und zähle die Punkte
    for gemeinde in gemeinden:
        # Filtere das GeoDataFrame nach der aktuellen Gemeinde
        gemeinde_gdf = input_gdf[input_gdf['gemeinde'] == gemeinde]

        # Generiere die Zielpunkte für jeden Punkt in dieser Gemeinde
        for index, row in gemeinde_gdf.iterrows():
            # Erstelle eine Passagier-Nummer für jeden Punkt (aufsteigend)
            passagier_nummer = index + 1  # Aufsteigende Passagier-Nummer

            # Zufällige Auswahl einer anderen Gemeinde als Ziel
            ziel_gemeinde = np.random.choice([g for g in gemeinden if g != gemeinde])

            # Zufällige Auswahl eines Zielpunktes in der Zielgemeinde
            ziel_gemeinde_gdf = gemeinden_zentral_gdfs if ziel_gemeinde in gemeinden_zentral_gdfs['GEMEINDE'].values \
                else (gemeinden_höhere_Dichte_gdfs if ziel_gemeinde in gemeinden_höhere_Dichte_gdfs[
                'GEMEINDE'].values else gemeinden_niedrige_Dichte_gdfs)

            ziel_punkt_index = np.random.choice(ziel_gemeinde_gdf[ziel_gemeinde_gdf['GEMEINDE'] == ziel_gemeinde].index)

            # Füge den Zielpunkt als neue Zeile zum DataFrame hinzu
            ziel_punkt = ziel_gemeinde_gdf.loc[ziel_punkt_index, 'geometry'].centroid
            new_rows.append({'geometry': ziel_punkt,
                             'gemeinde': ziel_gemeinde,
                             'passagier_nummer': passagier_nummer})

    # Konvertiere die neuen Zeilen in ein DataFrame
    new_rows_df = pd.DataFrame(new_rows)

    # Füge die neuen Zeilen dem ursprünglichen GeoDataFrame hinzu
    input_gdf = pd.concat([input_gdf, new_rows_df], ignore_index=True)

    return input_gdf

def add_destination_columns(input_gdf, gemeinden_zentral_gdfs, gemeinden_höhere_Dichte_gdfs,
                            gemeinden_niedrige_Dichte_gdfs):
    # Extrahiere die eindeutigen Gemeinden aus dem GeoDataFrame
    gemeinden = input_gdf['gemeinde'].unique()

    # Erstelle ein leeres DataFrame, um die neuen Zeilen hinzuzufügen
    new_rows = []

    # Erstelle ein Dictionary, um das Kontingent für jede Zielgemeinde zu verfolgen
    kontingent_dict = {gemeinde: len(gemeinde_gdf) for gemeinde, gemeinde_gdf in input_gdf.groupby('gemeinde')}

    # Iteriere über jede Gemeinde und zähle die Punkte
    for gemeinde in gemeinden:
        # Filtere das GeoDataFrame nach der aktuellen Gemeinde
        gemeinde_gdf = input_gdf[input_gdf['gemeinde'] == gemeinde]

        # Generiere die Zielpunkte für jeden Punkt in dieser Gemeinde
        for index, row in gemeinde_gdf.iterrows():
            # Überprüfe, ob es noch Zielgemeinden mit nicht erschöpftem Kontingent gibt
            remaining_gemeinden = [g for g in gemeinden if g != gemeinde and kontingent_dict[g] > 0]
            if len(remaining_gemeinden) == 0:
                break  # Beende die Schleife, wenn alle Kontingente erschöpft sind

            # Wähle eine Zielgemeinde aus den verbleibenden aus
            ziel_gemeinde = np.random.choice(remaining_gemeinden)

            # Reduziere das Kontingent für die Zielgemeinde um 1
            kontingent_dict[ziel_gemeinde] -= 1

            # Zufällige Auswahl eines Zielpunktes in der Zielgemeinde
            ziel_gemeinde_gdf = gemeinden_zentral_gdfs if ziel_gemeinde in gemeinden_zentral_gdfs['GEMEINDE'].values \
                else (gemeinden_höhere_Dichte_gdfs if ziel_gemeinde in gemeinden_höhere_Dichte_gdfs[
                'GEMEINDE'].values else gemeinden_niedrige_Dichte_gdfs)

            ziel_punkt_index = np.random.choice(ziel_gemeinde_gdf[ziel_gemeinde_gdf['GEMEINDE'] == ziel_gemeinde].index)

            # Erstelle eine Passagier-Nummer für jeden Punkt (aufsteigend)
            passagier_nummer = len(new_rows) + 1  # Aufsteigende Passagier-Nummer

            # Füge den Zielpunkt als neue Zeile zum DataFrame hinzu
            ziel_punkt = ziel_gemeinde_gdf.loc[ziel_punkt_index, 'geometry'].centroid
            new_rows.append({'geometry': ziel_punkt,
                             'gemeinde': ziel_gemeinde,
                             'passagier_nummer': passagier_nummer})

    # Konvertiere die neuen Zeilen in ein DataFrame
    new_rows_df = pd.DataFrame(new_rows)

    # Füge die neuen Zeilen dem ursprünglichen GeoDataFrame hinzu
    input_gdf = pd.concat([input_gdf, new_rows_df], ignore_index=True)

    return input_gdf

import pandas as pd
import numpy as np
import geopandas as gpd

def create_destination_gdf(input_gdf, gemeinden_zentral_gdfs, gemeinden_höhere_Dichte_gdfs,
                            gemeinden_niedrige_Dichte_gdfs):
    # Extrahiere die eindeutigen Gemeinden aus dem GeoDataFrame
    gemeinden = input_gdf['gemeinde'].unique()

    # Erstelle ein leeres DataFrame, um die neuen Zeilen hinzuzufügen
    new_rows = []

    # Erstelle ein Dictionary, um das Kontingent für jede Zielgemeinde zu verfolgen
    kontingent_dict = {gemeinde: len(gemeinde_gdf) for gemeinde, gemeinde_gdf in input_gdf.groupby('gemeinde')}

    # Iteriere über jede Gemeinde und zähle die Punkte
    for gemeinde in gemeinden:
        # Filtere das GeoDataFrame nach der aktuellen Gemeinde
        gemeinde_gdf = input_gdf[input_gdf['gemeinde'] == gemeinde]

        # Generiere die Zielpunkte für jeden Punkt in dieser Gemeinde
        for index, row in gemeinde_gdf.iterrows():
            # Überprüfe, ob es noch Zielgemeinden mit nicht erschöpftem Kontingent gibt
            remaining_gemeinden = [g for g in gemeinden if g != gemeinde and kontingent_dict[g] >= 0]
            if len(remaining_gemeinden) == 0:
                break  # Beende die Schleife, wenn alle Kontingente erschöpft sind

            # Wähle eine Zielgemeinde aus den verbleibenden aus
            ziel_gemeinde = np.random.choice(remaining_gemeinden)

            # Reduziere das Kontingent für die Zielgemeinde um 1
            kontingent_dict[ziel_gemeinde] -= 1

            # Zufällige Auswahl eines Zielpunktes in der Zielgemeinde
            ziel_gemeinde_gdf = gemeinden_zentral_gdfs if ziel_gemeinde in gemeinden_zentral_gdfs['GEMEINDE'].values \
                else (gemeinden_höhere_Dichte_gdfs if ziel_gemeinde in gemeinden_höhere_Dichte_gdfs[
                'GEMEINDE'].values else gemeinden_niedrige_Dichte_gdfs)

            ziel_punkt_index = np.random.choice(ziel_gemeinde_gdf[ziel_gemeinde_gdf['GEMEINDE'] == ziel_gemeinde].index)

            # Erstelle eine Passagier-Nummer für jeden Punkt (aufsteigend)
            passagier_nummer = len(new_rows) + 1  # Aufsteigende Passagier-Nummer

            # Füge den Zielpunkt als neue Zeile zum DataFrame hinzu
            ziel_punkt = ziel_gemeinde_gdf.loc[ziel_punkt_index, 'geometry'].centroid
            new_rows.append({'geometry': ziel_punkt,
                             'gemeinde': ziel_gemeinde,
                             'passagier_nummer': passagier_nummer})

    # Konvertiere die neuen Zeilen in ein DataFrame
    new_rows_df = pd.DataFrame(new_rows)

    # Erstelle ein GeoDataFrame aus den neuen Zeilen
    destination_gdf = gpd.GeoDataFrame(new_rows_df, geometry='geometry')

    return destination_gdf




def filter_null_timestamp(gdf):
    filtered_gdf = gdf[gdf['timestamp'].isnull()]
    return filtered_gdf


def create_destination_zuglinie_gdf(input_gdf, gemeinden_zentral_gdfs, gemeinden_höhere_Dichte_gdfs,
                                    gemeinden_niedrige_Dichte_gdfs, bahnhöfe_gdf):
    # Extrahiere die eindeutigen Gemeinden aus dem GeoDataFrame
    gemeinden = input_gdf['gemeinde'].unique()

    # Erstelle ein leeres DataFrame, um die neuen Zeilen hinzuzufügen
    new_rows = []

    # Erstelle ein Dictionary, um das Kontingent für jede Zielgemeinde zu verfolgen
    kontingent_dict = {gemeinde: len(gemeinde_gdf) for gemeinde, gemeinde_gdf in input_gdf.groupby('gemeinde')}

    # Erstelle ein Dictionary, um das Kontingent für die Bahnhöfe zu verfolgen
    bahnhof_kontingent_dict = {row['geometry']: len(input_gdf[input_gdf['geometry'] == row['geometry']]) for _, row in
                               bahnhöfe_gdf.iterrows()}

    # Iteriere über jede Gemeinde und zähle die Punkte
    for gemeinde in gemeinden:
        # Filtere das GeoDataFrame nach der aktuellen Gemeinde
        gemeinde_gdf = input_gdf[input_gdf['gemeinde'] == gemeinde]

        # Generiere die Zielpunkte für jeden Punkt in dieser Gemeinde
        for index, row in gemeinde_gdf.iterrows():
            # Überprüfe, ob der aktuelle Punkt ein Bahnhofspunkt ist
            if row['geometry'] in bahnhof_kontingent_dict and bahnhof_kontingent_dict[row['geometry']] > 0:
                # Zufällig entscheiden, ob der Punkt auf dem Bahnhof oder in der Zone verteilt wird
                if np.random.rand() < 0.5:
                    # Punkt bleibt auf dem Bahnhof
                    ziel_punkt = row['geometry']
                else:
                    # Punkt wird zufällig in den Zonen verteilt
                    remaining_gemeinden = [g for g in gemeinden if g != gemeinde and kontingent_dict[g] >= 0]
                    if len(remaining_gemeinden) > 0:
                        ziel_gemeinde = np.random.choice(remaining_gemeinden)
                        kontingent_dict[ziel_gemeinde] -= 1

                        ziel_gemeinde_gdf = gemeinden_zentral_gdfs if ziel_gemeinde in gemeinden_zentral_gdfs[
                            'GEMEINDE'].values \
                            else (gemeinden_höhere_Dichte_gdfs if ziel_gemeinde in gemeinden_höhere_Dichte_gdfs[
                            'GEMEINDE'].values else gemeinden_niedrige_Dichte_gdfs)

                        ziel_punkt_index = np.random.choice(
                            ziel_gemeinde_gdf[ziel_gemeinde_gdf['GEMEINDE'] == ziel_gemeinde].index)
                        ziel_punkt = ziel_gemeinde_gdf.loc[ziel_punkt_index, 'geometry'].centroid
                    else:
                        ziel_punkt = row['geometry']

                bahnhof_kontingent_dict[row['geometry']] -= 1
            else:
                # Überprüfe, ob es noch Zielgemeinden mit nicht erschöpftem Kontingent gibt
                remaining_gemeinden = [g for g in gemeinden if g != gemeinde and kontingent_dict[g] >= 0]
                if len(remaining_gemeinden) == 0:
                    break  # Beende die Schleife, wenn alle Kontingente erschöpft sind

                # Wähle eine Zielgemeinde aus den verbleibenden aus
                ziel_gemeinde = np.random.choice(remaining_gemeinden)

                # Reduziere das Kontingent für die Zielgemeinde um 1
                kontingent_dict[ziel_gemeinde] -= 1

                # Zufällige Auswahl eines Zielpunktes in der Zielgemeinde
                ziel_gemeinde_gdf = gemeinden_zentral_gdfs if ziel_gemeinde in gemeinden_zentral_gdfs['GEMEINDE'].values \
                    else (gemeinden_höhere_Dichte_gdfs if ziel_gemeinde in gemeinden_höhere_Dichte_gdfs[
                    'GEMEINDE'].values else gemeinden_niedrige_Dichte_gdfs)

                ziel_punkt_index = np.random.choice(
                    ziel_gemeinde_gdf[ziel_gemeinde_gdf['GEMEINDE'] == ziel_gemeinde].index)
                ziel_punkt = ziel_gemeinde_gdf.loc[ziel_punkt_index, 'geometry'].centroid

            # Erstelle eine Passagier-Nummer für jeden Punkt (aufsteigend)
            passagier_nummer = len(new_rows) + 1  # Aufsteigende Passagier-Nummer

            # Füge den Zielpunkt als neue Zeile zum DataFrame hinzu
            new_rows.append({'geometry': ziel_punkt,
                             'gemeinde': ziel_gemeinde if row['geometry'] not in bahnhof_kontingent_dict else gemeinde,
                             'passagier_nummer': passagier_nummer})

    # Konvertiere die neuen Zeilen in ein DataFrame
    new_rows_df = pd.DataFrame(new_rows)

    # Erstelle ein GeoDataFrame aus den neuen Zeilen
    destination_gdf = gpd.GeoDataFrame(new_rows_df, geometry='geometry')

    return destination_gdf
