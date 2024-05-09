import subprocess
from main_functions import *
import pandas as pd
import importlib

def run_simulation(num_simulations):
    scenario_module = importlib.import_module('scenario')
    bus_model = importlib.import_module('busline')
    ODPT_model = importlib.import_module('ODPT_model')
    results = importlib.import_module('results')

    # Ergebnisse für den ersten Durchlauf sammeln
    scenario_module.scenario()
    bus_model.busline()
    ODPT_model.ODPT()
    df = results.results()

    # Ergebnisse für die weiteren Durchläufe holen und an das DataFrame anhängen
    for _ in range(1, num_simulations):
        scenario_module.scenario()
        bus_model.busline()
        ODPT_model.ODPT()
        current_results = results.results()
        df = pd.concat([df, current_results], ignore_index=True)

    costs = results.costs(df)
    value = results.value_created(df)

    return df, costs, value




if __name__ == "__main__":
    num_simulations = int(input("Wie oft möchten Sie das Szenario ausführen? "))
    combined_results, costs, value = run_simulation(num_simulations)
    print(combined_results)
    print(costs)
    print(value)
