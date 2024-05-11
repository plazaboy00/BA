import pandas as pd
import numpy as np
from busline import busline
from ODPT_model import ODPT


def results():
    # Erstelle Tabelle mit den Rohdaten

    # Provisorische Werte
    #bus_time = 55

    busline_passengers, busline_km, busline_total_travel_time, bus_passengers_df = busline()
    #print(busline_passengers, busline_km, busline_total_travel_time)

    ODPT_passengers, ODPT_km, ODPT_total_travel_time, ODPT_passengers_df = ODPT()
    #print(ODPT_passengers, ODPT_km, ODPT_total_travel_time)

    mean_travel_time_per_passenger_bus = bus_passengers_df['travel_time'].mean()
    mean_travel_time_per_passenger_ODPT = ODPT_passengers_df['travel_time'].mean()

    data = {
        "busline_km": busline_km,
        "busline_passengers": busline_passengers,
        "busline_total_travel_time": busline_total_travel_time,
        "mean_travel_time_per_passenger_bus": mean_travel_time_per_passenger_bus,
        "ODPT_km": ODPT_km,
        "ODPT_passengers": ODPT_passengers,
        "ODPT_total_travel_time": ODPT_total_travel_time,
        "mean_travel_time_per_passenger_ODPT": mean_travel_time_per_passenger_ODPT
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
        costs = costs_per_100 / 100

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

    mean_km_bus = total_km_bus / len(df)
    mean_km_ODPT = total_km_ODPT / len(df)

    bus_costs = costs_per_a_km(mean_km_bus)
    ODPT_costs = costs_per_a_km(mean_km_ODPT)

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
    print(df)

    return df

def value_created(df):
    def value_of_vtts(number, travel_time):
        h_per_day = 12
        days_per_year = 365
        CHF_per_h = 14
        total_time_per_h = travel_time * number * CHF_per_h
        value = total_time_per_h * h_per_day * days_per_year
        return value

    #print(df.head())

    total_passenger_bus = df['busline_passengers'].sum()
    total_passenger_ODPT = df['ODPT_passengers'].sum()
    #print('total p', total_passenger_ODPT)

    num_scenarios = len(df)
    #print(num_scenarios)
    mean_passenger_bus = total_passenger_bus / len(df)
    mean_passenger_ODPT = total_passenger_ODPT / len(df)

    mean_travel_time_bus = df['mean_travel_time_per_passenger_bus'].sum() / len(df)
    mean_travel_time_ODPT = df['mean_travel_time_per_passenger_ODPT'].sum() / len(df)
    #print('mean', mean_travel_time_ODPT)

    value_bus = value_of_vtts(mean_passenger_bus, mean_travel_time_bus)
    #print('wert bus', value_bus)
    value_ODPT = value_of_vtts(mean_passenger_ODPT, mean_travel_time_ODPT)

    data = {
        "Bus income": value_bus,
        "ODPT income": value_ODPT
    }

    # Erstelle einen DataFrame aus den Daten
    df = pd.DataFrame([data])
    #print(df)

    return df


