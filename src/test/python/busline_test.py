import random
from test_scenario import scenario


def busline():
    num_passengers = scenario()
    #print('bus passagiere:', num_passengers)
    total_distance_bus = random.randint(30, 35)
    travel_time_bus = 55

    return num_passengers, total_distance_bus, travel_time_bus


#if __name__ == "__main__":
    #main()
