import subprocess
from main_functions import *
import pandas as pd
import importlib

ROOT_FILES = 'C:/Users/Linus/PycharmProjects/BA/'
ROOT_DOCS = 'src/main/resources/Dokumente/'

def run_simulation(num_simulations):
    scenario_module = importlib.import_module('scenario')
    bus_model = importlib.import_module('busline')
    ODPT_model = importlib.import_module('ODPT_model')
    results = importlib.import_module('results')
    roadnetwork = importlib.import_module('roadmap')

    # Scenario Parameter
    stunden_verkehrstag = 18

    # Bus Parameter
    max_capacity_bus = 31
    waiting_time = 20

    # ODPT Parameter
    max_capacity_odpt = 31
    max_travel_time_per_section = 900
    # Ergebnisse für den ersten Durchlauf sammeln
    scenario_module.scenario(stunden_verkehrstag)
    roadnetwork.load_roadmap()
    #bus_model.busline(max_capacity)
    #ODPT_model.odpt(max_capacity, max_travel_time_per_section)
    df = results.results(max_capacity_bus, waiting_time, max_capacity_odpt, max_travel_time_per_section)

    # Ergebnisse für die weiteren Durchläufe holen und an das DataFrame anhängen
    for _ in range(1, num_simulations):
        scenario_module.scenario(stunden_verkehrstag)
        #bus_model.busline(max_capacity)
        #ODPT_model.odpt(max_capacity, max_travel_time_per_section)
        current_results = results.results(max_capacity_bus, max_capacity_odpt, max_travel_time_per_section)
        df = pd.concat([df, current_results], ignore_index=True)

    costs = results.costs(df)
    value = results.value_created(df)

    return df, costs, value




if __name__ == "__main__":
    num_simulations = int(input("Wie oft möchten Sie das Szenario ausführen? "))
    combined_results, costs, value = run_simulation(num_simulations)
    # Pfad zur Ausgabedatei
    csv_path_rohdaten = ROOT_FILES + ROOT_DOCS + "Rohdaten.csv"
    combined_results.to_csv(csv_path_rohdaten, index=False)
    csv_path_costs = ROOT_FILES + ROOT_DOCS + "Kosten&Einnahmen.csv"
    costs.to_csv(csv_path_costs, index=False)
    print(combined_results)
    print(costs)
    print(value)
