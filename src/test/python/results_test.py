import pandas as pd
import numpy as np
from busline_test import busline
from ODPT_test import ODPT


def results():
    # Erstelle Tabelle mit den Rohdaten

    # Provisorische Werte
    #bus_time = 55

    busline_passengers, busline_km, busline_total_travel_time = busline()
    #print(busline_passengers, busline_km, busline_total_travel_time)

    ODPT_passengers, ODPT_km, ODPT_total_travel_time = ODPT()
    #print(ODPT_passengers, ODPT_km, ODPT_total_travel_time)

    data = {
        "busline_km": busline_km,
        "busline_passengers": busline_passengers,
        "busline_total_travel_time": busline_total_travel_time,
        "ODPT_km": ODPT_km,
        "ODPT_passengers": ODPT_passengers,
        "ODPT_total_travel_time": ODPT_total_travel_time
    }

    # Erstelle einen DataFrame aus den Daten
    df = pd.DataFrame([data])

    return df

def costs(df):
    def costs_per_a_km(km):
        CHF_per_100_Fzkm = 69.07
        h_per_day = 12
        days_per_year = 365
        mean_km = np.mean(km)
        km_per_a = mean_km * h_per_day * days_per_year
        costs_per_100 = km_per_a * CHF_per_100_Fzkm
        costs = costs_per_100 * 100

        return costs

    def income_per_passenger(num_passenger):
        h_per_day = 12
        days_per_year = 365
        price = 5  # CHF per trip
        income_per_p = num_passenger * price
        mean_p = np.mean(num_passenger)
        p_per_a = mean_p * h_per_day * days_per_year
        income_per_a = p_per_a * income_per_p

        return income_per_a

    df = df
    total_km_bus = df['busline_km'].sum()
    total_km_ODPT = df['ODPT_km'].sum()

    bus_costs = costs_per_a_km(total_km_bus)
    ODPT_costs = costs_per_a_km(total_km_ODPT)

    total_passenger_bus = df['busline_passengers'].sum()
    total_passenger_ODPT = df['ODPT_passengers'].sum()

    bus_income = income_per_passenger(total_passenger_bus)
    ODPT_income = income_per_passenger(total_passenger_ODPT)






    data = {
        "Bus costs": bus_costs,
        "ODPT costs": ODPT_costs,
        "Bus income": bus_income,
        "ODPT income": ODPT_income
    }

    # Erstelle einen DataFrame aus den Daten
    df = pd.DataFrame([data])

    return df


#if __name__ == "__main__":
    #main()


