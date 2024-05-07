from test_scenario import scenario
import random
def ODPT():
    successful_trips = int(scenario() / 2)
    #print('ODPT passagiere:', successful_trips)
    total_distance_ODPT = random.randint(30, 60)
    travel_time_ODPT = random.randint(50, 60)

    return successful_trips, total_distance_ODPT, travel_time_ODPT


#if __name__ == "__main__":
    #main()
