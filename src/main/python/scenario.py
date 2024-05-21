from geo_data_processing import *
from plot import *


def scenario(stunden_verkehrstag):
    # Erstelle Root zum Hauptordner
    ROOT_FILES = 'C:/Users/Linus/PycharmProjects/BA/'
    ROOT_RESOURCE = 'src/main/resources/QGIS/Nutzungsplan/'
    ROOT_DOCS = 'src/main/resources/Dokumente/'
    shapefile_paths = [ROOT_FILES + 'src/test/resources/input/Gebaut.shp', 'C:/Users/Linus/Documents/W1Gebaut.shp']
    # Füge die verschiedene aus dem Inputornder Geo Files zusammen und speichere sie als gdf

    gemeinden_gdfs = []
    geo_files_tief = ['Gebaut.shp', 'W1Gebaut.shp', 'W30.gpkg', 'W2Uster.gpkg']
    geo_files_hoch = ['W2Gebaut.gpkg', 'W2.gpkg', 'W3Uster.gpkg', 'W60.gpkg']
    geo_files_zentral = ['Zentrum&Gewerbe.shp', 'ZonenOe.shp', 'Zentrum.gpkg', 'ZentrumUster.gpkg', 'ZentrumEgg.gpkg']

    gdf_tiefe_Dichte = create_geo_dataframe(geo_files_tief)
    gdf_hohe_Dichte = create_geo_dataframe(geo_files_hoch)
    gdf_zentrale_Dichte = create_geo_dataframe(geo_files_zentral)

    #Importiere die Datensätze für das Verkehrsmodell, das Strassenetz und der Gemeindengrenzen
    ROOT_RESOURCE_VERKEHRSMODELL = 'src/main/resources/Verkehrsmodell/'
    DATEN_VERKEHRSMODELL = pd.read_csv(ROOT_FILES + ROOT_RESOURCE_VERKEHRSMODELL + 'KTZH_00001982_00003903(1).csv')

    ROOT_RESOURCE_GEMEINDENGRENZEN = 'src/main/resources/QGIS/Gemeindegrenzen/'
    DATEN_GEMEINDENGRENZEN = gpd.read_file(ROOT_FILES + ROOT_RESOURCE_GEMEINDENGRENZEN + 'Gemeindegrenzen.shp')

    ROOT_RESOURCE_STRASSENNETZ = 'src/main/resources/QGIS/Strassen/'
    DATEN_STRASSENNETZ = gpd.read_file(ROOT_FILES + ROOT_RESOURCE_STRASSENNETZ + 'AlleStrassen.shp')

    # Pfad zur Shapefile-Datei mit den Bushaltestellen
    ROOT_ODPT_stops = 'src/main/resources/ODPT/'
    shapefile_path = ROOT_FILES + ROOT_ODPT_stops + "ODPTSTOPS.shp"

    # Laden der Bushaltestellen als GeoDataFrame
    ODPT_stops = gpd.read_file(shapefile_path)

    # Erstellen der Nachfragepunkte zu den Bahnhöfen
    gemeinden_zuglinie_Meilen = ['Meilen', 'Zollikon', 'Küsnacht (ZH)', 'Erlenbach (ZH)', 'Herrliberg',
                                 'Uetikon am See', 'Männedorf', 'Stäfa', 'Hombrechtikon']
    zielgemeinden_zuglinie_meilen = ['Meilen',  'Zollikon', 'Küsnacht (ZH)', 'Erlenbach (ZH)', 'Herrliberg',
                                     'Uetikon am See', 'Männedorf', 'Stäfa', 'Hombrechtikon']
    gemeinden_zuglinie_egg = ['Egg',  'Zollikon', 'Küsnacht (ZH)', 'Maur', 'Zumikon']
    zielgemeinden_zuglinie_egg = ['Egg',  'Zollikon', 'Küsnacht (ZH)', 'Maur', 'Zumikon']
    gemeinden_zuglinie_uster = ['Uster', 'Dübendorf', 'Greifensee', 'Schwerzenbach', 'Seegräben', 'Wetzikon',
                                'Bubikon', 'Rüti (ZH)']
    zielgemeinden_zuglinie_uster = ['Uster', 'Dübendorf', 'Greifensee', 'Schwerzenbach', 'Seegräben',
                                    'Wetzikon', 'Bubikon', 'Rüti (ZH)']
    gewuenschte_kategorien_zuglinie = ['Verkehrsaufkommen']
    gewuenschte_verkehrsmittel_zuglinie = ['oev']
    gewuenschtes_jahr_zuglinie = 2018

    #Analyse des Verkehrsmodell in den Gemeinden
    gewuenschte_gemeinden = ['Meilen', 'Egg', 'Uster', 'Uetikon am See']
    gewuenschte_zielnamen = ['Meilen', 'Egg', 'Uster', 'Uetikon am See']
    gewuenschte_kategorien = ['Verkehrsaufkommen']
    gewuenschte_verkehrsmittel = ['oev']
    gewuenschtes_jahr = 2018
    #DATENSATZ_VERKEHR = DATEN_VERKEHRSMODELL

    DATEN_FILTERED = filter_data(DATEN_VERKEHRSMODELL, gewuenschtes_jahr,
                                 gewuenschte_gemeinden, gewuenschte_zielnamen,
                                 gewuenschte_kategorien, gewuenschte_verkehrsmittel)

    # Filtern der Daten für jeden Zielort
    daten_meilen = filter_target_data(DATEN_FILTERED, 'Meilen')
    daten_egg = filter_target_data(DATEN_FILTERED, 'Egg')
    daten_uster = filter_target_data(DATEN_FILTERED, 'Uster')
    daten_uetikon = filter_target_data(DATEN_FILTERED, 'Uetikon am See')

    # Annahme: Vordefinierte Werte für stunden_verkehrstag und prozent_verteilung_hoch/mittel/niedrig
    #stunden_verkehrstag = 18
    prozent_verteilung_hoch = 0.5
    prozent_verteilung_mittel = 0.3
    prozent_verteilung_niedrig = 0.2

    Anzahl_Meilen_Egg_oev = filter_and_calculate_traffic_data(
        DATEN_VERKEHRSMODELL, 'Meilen', 'Egg', 'oev', 2018, 'Verkehrsaufkommen'
    )
    Anzahl_Meilen_Egg_miv = filter_and_calculate_traffic_data(
        DATEN_VERKEHRSMODELL, 'Meilen', 'Egg', 'miv', 2018, 'Verkehrsaufkommen'
    )
    Anzahl_Uetikon_Egg_oev = filter_and_calculate_traffic_data(
        DATEN_VERKEHRSMODELL, 'Uetikon am See', 'Egg', 'oev', 2018, 'Verkehrsaufkommen'
    )
    Anzahl_Uetikon_Egg_miv = filter_and_calculate_traffic_data(
        DATEN_VERKEHRSMODELL, 'Uetikon am See', 'Egg', 'miv', 2018, 'Verkehrsaufkommen'
    )
    Anzahl_oetwil_maennedorf_miv = filter_and_calculate_traffic_data(
        DATEN_VERKEHRSMODELL, 'Oetwil am See', 'Männedorf', 'miv', 2018, 'Verkehrsaufkommen'
    )
    Anzahl_oetwil_maennedorf_oev = filter_and_calculate_traffic_data(
        DATEN_VERKEHRSMODELL, 'Oetwil am See', 'Männedorf', 'oev', 2018, 'Verkehrsaufkommen'
    )
    modal_split_oev_Oetwil = filter_and_calculate_traffic_data(
        DATEN_VERKEHRSMODELL, 'Oetwil am See', 'Männedorf', 'oev', 2018, 'Modal Split'
    )
    modal_split_oev_oetwil_uster = filter_and_calculate_traffic_data(
        DATEN_VERKEHRSMODELL, 'Oetwil am See', 'Uster', 'oev', 2018, 'Modal Split'
    )

    DATEN_FILTERED_zuglinie_meilen = filter_data(DATEN_VERKEHRSMODELL, gewuenschtes_jahr_zuglinie,
                                                 gemeinden_zuglinie_Meilen, zielgemeinden_zuglinie_meilen,
                                                 gewuenschte_kategorien_zuglinie,
                                                 gewuenschte_verkehrsmittel_zuglinie)
    daten_meilen_zuglinie = filter_target_data(DATEN_FILTERED_zuglinie_meilen, 'Meilen')
    nachfrage_meilen_zuglinie, nachfrage_meilen_zuglinie_bahnhof, \
        nachfrage_meilen_zentral, nachfrage_meilen_höhere_Dichte, nachfrage_meilen_niedrige_Dichte \
        = calculate_demand_bahnhof(daten_meilen, daten_meilen_zuglinie, stunden_verkehrstag, \
                                   prozent_verteilung_hoch, prozent_verteilung_mittel, prozent_verteilung_niedrig)

    DATEN_FILTERED_zuglinie_egg = filter_data(DATEN_VERKEHRSMODELL, gewuenschtes_jahr_zuglinie,
                                              gemeinden_zuglinie_egg, zielgemeinden_zuglinie_egg,
                                              gewuenschte_kategorien_zuglinie, gewuenschte_verkehrsmittel_zuglinie)
    daten_egg_zuglinie = filter_target_data(DATEN_FILTERED_zuglinie_egg, 'Egg')

    DATEN_FILTERED_zuglinie_uster = filter_data(DATEN_VERKEHRSMODELL, gewuenschtes_jahr_zuglinie,
                                                gemeinden_zuglinie_uster, zielgemeinden_zuglinie_uster,
                                                gewuenschte_kategorien_zuglinie, gewuenschte_verkehrsmittel_zuglinie)
    daten_uster_zuglinie = filter_target_data(DATEN_FILTERED_zuglinie_uster, 'Uster')

    # Berechne das neue Verkehrsaufkommen für die Gemeinden Meilen und Uetikon
    neues_verkehrsaufkommen_oev_Meilen_Egg = berechne_verkehrsaufkommen(
        Anzahl_Meilen_Egg_oev, Anzahl_Meilen_Egg_miv, modal_split_oev_Oetwil) - Anzahl_Meilen_Egg_oev

    neues_verkehrsaufkommen_oev_Uetikon_Egg = berechne_verkehrsaufkommen(
        Anzahl_Uetikon_Egg_oev, Anzahl_Uetikon_Egg_miv, modal_split_oev_Oetwil) - Anzahl_Uetikon_Egg_oev

    nachfrage_meilen_zuglinie, nachfrage_meilen_zuglinie_bahnhof, \
        nachfrage_meilen_zentral, nachfrage_meilen_höhere_Dichte, nachfrage_meilen_niedrige_Dichte \
        = calculate_demand_bahnhof(daten_meilen, daten_meilen_zuglinie, stunden_verkehrstag, \
                                   prozent_verteilung_hoch, prozent_verteilung_mittel, prozent_verteilung_niedrig)

    nachfrage_egg_zuglinie, nachfrage_egg_zuglinie_bahnhof, \
        nachfrage_egg_zentral, nachfrage_egg_höhere_Dichte, nachfrage_egg_niedrige_Dichte \
        = calculate_demand_bahnhof(daten_egg, daten_egg_zuglinie, stunden_verkehrstag, \
                                   prozent_verteilung_hoch, prozent_verteilung_mittel, prozent_verteilung_niedrig)

    nachfrage_uster_zuglinie, nachfrage_uster_zuglinie_bahnhof, \
        nachfrage_uster_zentral, nachfrage_uster_höhere_Dichte, nachfrage_uster_niedrige_Dichte \
        = calculate_demand_bahnhof(daten_uster, daten_uster_zuglinie, stunden_verkehrstag, \
                                   prozent_verteilung_hoch, prozent_verteilung_mittel, prozent_verteilung_niedrig)

    nachfrage_uetikon, nachfrage_uetikon_zentral,\
        nachfrage_uetikon_höhere_Dichte, nachfrage_uetikon_niedrige_Dichte =\
        calculate_new_demand(daten_uetikon, neues_verkehrsaufkommen_oev_Uetikon_Egg, stunden_verkehrstag,
                         prozent_verteilung_hoch, prozent_verteilung_mittel,
                         prozent_verteilung_niedrig)

    # Setze die Zeitstempel für die Nachfragepunkte
    start_timestamp = pd.Timestamp('2018-04-20 09:00:00')
    end_timestamp = pd.Timestamp('2018-04-20 10:00:00')

    # Verteile die Nachfragepunkte in den Gemeinden
    (nachfrage_meilen_zentral_pos, nachfrage_meilen_zentral_timestamps), \
        (nachfrage_meilen_höhere_Dichte_pos, nachfrage_meilen_höhere_Dichte_timestamps), \
        (nachfrage_meilen_niedrige_Dichte_pos, nachfrage_meilen_niedrige_Dichte_timestamps), \
        nachfragepunkte_bahnhof_timestamps = \
        verteile_nachfragepunkte_bahnhof('Meilen', nachfrage_meilen_zentral,
                                 nachfrage_meilen_höhere_Dichte,
                                 nachfrage_meilen_niedrige_Dichte,
                                 nachfrage_meilen_zuglinie_bahnhof,
                                 gdf_zentrale_Dichte, gdf_hohe_Dichte,
                                 gdf_tiefe_Dichte, start_timestamp, end_timestamp)

    (nachfrage_egg_zentral_pos, nachfrage_egg_zentral_timestamps), \
        (nachfrage_egg_höhere_Dichte_pos, nachfrage_egg_höhere_Dichte_timestamps), \
        (nachfrage_egg_niedrige_Dichte_pos, nachfrage_egg_niedrige_Dichte_timestamps), \
        nachfragepunkte_bahnhof_timestamps = \
        verteile_nachfragepunkte_bahnhof('Egg', nachfrage_egg_zentral,
                                 nachfrage_egg_höhere_Dichte,
                                 nachfrage_egg_niedrige_Dichte,
                                 nachfrage_egg_zuglinie_bahnhof,
                                 gdf_zentrale_Dichte, gdf_hohe_Dichte,
                                 gdf_tiefe_Dichte, start_timestamp, end_timestamp)

    (nachfrage_uster_zentral_pos, nachfrage_uster_zentral_timestamps), \
        (nachfrage_uster_höhere_Dichte_pos, nachfrage_uster_höhere_Dichte_timestamps), \
        (nachfrage_uster_niedrige_Dichte_pos, nachfrage_uster_niedrige_Dichte_timestamps), \
        nachfragepunkte_bahnhof_timestamps = \
        verteile_nachfragepunkte_bahnhof('Uster', nachfrage_uster_zentral,
                                 nachfrage_uster_höhere_Dichte,
                                 nachfrage_uster_niedrige_Dichte,
                                 nachfrage_uster_zuglinie_bahnhof,
                                 gdf_zentrale_Dichte, gdf_hohe_Dichte,
                                 gdf_tiefe_Dichte, start_timestamp, end_timestamp)

    (nachfrage_uetikon_zentral_pos, nachfrage_uetikon_zentral_timestamps), \
    (nachfrage_uetikon_höhere_Dichte_pos, nachfrage_uetikon_höhere_Dichte_timestamps), \
    (nachfrage_uetikon_niedrige_Dichte_pos, nachfrage_uetikon_niedrige_Dichte_timestamps) = \
        verteile_nachfragepunkte('Uetikon am See', nachfrage_uetikon_zentral,
                                    nachfrage_uetikon_höhere_Dichte,
                                    nachfrage_uetikon_niedrige_Dichte,
                                    gdf_zentrale_Dichte, gdf_hohe_Dichte,
                                    gdf_tiefe_Dichte, start_timestamp, end_timestamp)

    # Rufe die Funktion auf, um die Daten vorzubereiten
    meilen_punkte_df = prepare_demand_data_bahnhof(gdf_zentrale_Dichte, gdf_hohe_Dichte, gdf_tiefe_Dichte,
                                           nachfrage_meilen_zentral_pos, nachfrage_meilen_höhere_Dichte_pos,
                                           nachfrage_meilen_niedrige_Dichte_pos, nachfrage_meilen_zentral_timestamps,
                                           nachfrage_meilen_höhere_Dichte_timestamps,
                                           nachfrage_meilen_niedrige_Dichte_timestamps,
                                           'Meilen', ODPT_stops, nachfragepunkte_bahnhof_timestamps)

    egg_punkte_df = prepare_demand_data_bahnhof(gdf_zentrale_Dichte, gdf_hohe_Dichte, gdf_tiefe_Dichte,
                                        nachfrage_egg_zentral_pos, nachfrage_egg_höhere_Dichte_pos,
                                        nachfrage_egg_niedrige_Dichte_pos, nachfrage_egg_zentral_timestamps,
                                        nachfrage_egg_höhere_Dichte_timestamps,
                                        nachfrage_egg_niedrige_Dichte_timestamps,
                                        'Egg', ODPT_stops, nachfragepunkte_bahnhof_timestamps)

    uster_punkte_df = prepare_demand_data_bahnhof(gdf_zentrale_Dichte, gdf_hohe_Dichte, gdf_tiefe_Dichte,
                                          nachfrage_uster_zentral_pos, nachfrage_uster_höhere_Dichte_pos,
                                          nachfrage_uster_niedrige_Dichte_pos, nachfrage_uster_zentral_timestamps,
                                          nachfrage_uster_höhere_Dichte_timestamps,
                                          nachfrage_uster_niedrige_Dichte_timestamps,
                                          'Uster', ODPT_stops, nachfragepunkte_bahnhof_timestamps)

    uetikon_punkte_df = prepare_demand_data(gdf_zentrale_Dichte, gdf_hohe_Dichte, gdf_tiefe_Dichte,
                                           nachfrage_uetikon_zentral_pos, nachfrage_uetikon_höhere_Dichte_pos,
                                           nachfrage_uetikon_niedrige_Dichte_pos, nachfrage_uetikon_zentral_timestamps,
                                           nachfrage_uetikon_höhere_Dichte_timestamps, nachfrage_uetikon_niedrige_Dichte_timestamps,
                                           'Uetikon am See')

    # Verwendung von aussagekräftigen Variablennamen und Inline-Kommentaren
    alle_punkte_df = pd.concat([egg_punkte_df, uster_punkte_df, meilen_punkte_df, uetikon_punkte_df], ignore_index=True)
    alle_punkte_df_with_passenger_numbers = add_passenger_numbers(alle_punkte_df)

    alle_punkte_df_with_passenger_numbers.to_file(ROOT_FILES + ROOT_DOCS + "Nachfrage_bahnhof.geojson", driver='GeoJSON')

    # Plotten der Nachfrageverteilung
    #plot_demand_distribution(DATEN_GEMEINDENGRENZEN, gdf_zentrale_Dichte,
    # gdf_hohe_Dichte, gdf_tiefe_Dichte,
    # DATEN_STRASSENNETZ, alle_punkte_df_with_passenger_numbers)
    # Beispielaufruf:
    new_destination_gdf = create_destination_zuglinie_gdf_neu(alle_punkte_df_with_passenger_numbers, gdf_zentrale_Dichte, gdf_hohe_Dichte,
                                                 gdf_tiefe_Dichte, ODPT_stops)
    # Speichern der GeoDataFrame als GeoJSON-Datei
    new_destination_gdf.to_file(ROOT_FILES + ROOT_DOCS + "Ziele_bahnhof.geojson", driver='GeoJSON')

    # Anwenden der Funktion für das Hinzufügen von Zielspalten
    output_gdf = add_destination_columns(alle_punkte_df_with_passenger_numbers, gdf_zentrale_Dichte,
                                          gdf_hohe_Dichte, gdf_tiefe_Dichte)

    # Speichern der GeoDataFrame als GeoJSON-Datei
    #output_gdf.to_file(ROOT_FILES + ROOT_DOCS + "output.geojson", driver='GeoJSON')

    destination_gdf = filter_null_timestamp(output_gdf)

    #plot_demand_distribution(DATEN_GEMEINDENGRENZEN, gdf_zentrale_Dichte,
    # gdf_hohe_Dichte, gdf_tiefe_Dichte,
    # DATEN_STRASSENNETZ, destination_gdf)

stunden_verkehrstag = 18
scenario(stunden_verkehrstag)

