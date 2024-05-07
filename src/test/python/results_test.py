import pandas as pd
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
    df = df
    return df


#if __name__ == "__main__":
    #main()


