from test_scenario import scenario
import random
import pandas as pd
def ODPT():
    successful_trips = int(scenario() / 2)
    #print('ODPT passagiere:', successful_trips)
    total_distance_ODPT = random.randint(30, 60)
    travel_time_ODPT = random.randint(50, 60)

    data = {
        'origin': [227551157, 35831131, 101780924, 3104818251, 2153072108, 352769862, 355232188, 469243808],
        'destination': [393962506, 35830593, 2504897137, 1251070885, 10968187754, 1605601293, 264890212, 7102085105],
        'id': [17, 0, 6, 2, 8, 9, 10, 1],
        'travel_time': [6.958333, 5.698333, 12.52, 9.025, 12.663333, 13.605, 6.265, 7.363333]
    }

    passengers_df = pd.DataFrame(data)

    return successful_trips, total_distance_ODPT, travel_time_ODPT, passengers_df


#if __name__ == "__main__":
    #main()
