import subprocess
import pandas as pd
import importlib
#from results_test import process_results


def run_simulation(num_simulations):
    scenario_module = importlib.import_module('test_scenario')
    bus_model = importlib.import_module('busline_test')
    ODPT_model = importlib.import_module('ODPT_test')
    results = importlib.import_module('results_test')

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

    return df, costs


if __name__ == "__main__":
    num_simulations = int(input("Wie oft möchten Sie das Szenario ausführen? "))
    combined_results = run_simulation(num_simulations)
    print(combined_results)


