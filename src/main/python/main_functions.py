import subprocess
def run_scenario():
    subprocess.run(["python", "scenario.py"])


def run_model1():
    subprocess.run(["python", "busline.py"])


def run_model2():
    subprocess.run(["python", "ODPT_model.py"])


def save_results(results):
    with open("results.txt", "a") as file:
        file.write(results + "\n")

def run_simulation(num_simulations):
    results_list = []
    for _ in range(num_simulations):
        run_scenario()
        run_model1()
        run_model2()
        # Nehmen wir an, dass du die Ergebnisse aus den Modellen hier erhältst
        # und sie in einer Variable `results` gespeichert sind
        results = "Beispielergebnisse"  # Hier musst du deine tatsächlichen Ergebnisse einfügen
        results_list.append(results)

    return results_list