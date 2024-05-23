import subprocess
from main_functions import *
import pandas as pd
import importlib

ROOT_FILES = 'C:/Users/Linus/PycharmProjects/BA/'
ROOT_DOCS = 'src/main/resources/Dokumente/'

def run_simulation(num_simulations, number_vehicles):
    scenario_module = importlib.import_module('scenario')
    bus_model = importlib.import_module('busline')
    ODPT_model = importlib.import_module('ODPT_model')
    results = importlib.import_module('results')
    roadnetwork = importlib.import_module('roadmap')

    # Scenario Parameter
    stunden_verkehrstag = 18
    tage_vekehrsjahr = 365

    # Bus Parameter
    max_capacity_bus = 31
    waiting_time = 20

    # ODPT Parameter
    max_capacity_odpt = 5
    max_travel_time_per_section = 900
    # Ergebnisse für den ersten Durchlauf sammeln
    scenario_module.scenario(stunden_verkehrstag)
    roadnetwork.load_roadmap()
    #bus_model.busline(max_capacity_bus, waiting_time)
    #ODPT_model.odpt(max_capacity_odpt, max_travel_time_per_section, number_vehicles)
    df = results.results(max_capacity_bus, waiting_time, max_capacity_odpt, max_travel_time_per_section, number_vehicles)

    # Ergebnisse für die weiteren Durchläufe holen und an das DataFrame anhängen
    for _ in range(1, num_simulations):
        scenario_module.scenario(stunden_verkehrstag)
        #bus_model.busline(max_capacity)
        #ODPT_model.odpt(max_capacity, max_travel_time_per_section)
        current_results = results.results(max_capacity_bus, waiting_time, max_capacity_odpt, max_travel_time_per_section, number_vehicles)
        df = pd.concat([df, current_results], ignore_index=True)

    costs = results.costs(df, stunden_verkehrstag, tage_vekehrsjahr)
    #value = results.value_created(df)

    return df, costs




if __name__ == "__main__":
    num_simulations = int(input("Wie viele Simulationen möchte ich durchführen? "))
    min_vehicle = int(input("Wie viele Fahrzeuge sollen minimal verwendet werden? "))
    max_vehicle = int(input("Wie viele Fahrzeuge sollen maximal verwendet werden? "))

    for vehicles in range(min_vehicle, max_vehicle):
        combined_results, costs = run_simulation(num_simulations, vehicles)
        # Pfad zur Ausgabedatei
        csv_path_rohdaten = ROOT_FILES + ROOT_DOCS + "Rohdaten" + str(vehicles) + ".csv"
        combined_results.to_csv(csv_path_rohdaten, index=False)
        csv_path_costs = ROOT_FILES + ROOT_DOCS + "Kosten&Einnahmen" + str(vehicles) + ".csv"
        costs.to_csv(csv_path_costs, index=False)
        print(combined_results)
        print(costs)


