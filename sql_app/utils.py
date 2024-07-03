import threading
import random
from datetime import datetime, time as dt_time, timezone, timedelta

lock = threading.Lock()


def get_random_city(cities):
    keys = list(cities.keys())

    while True:
        with lock:
            if all(city['taken'] for city in cities.values()):
                return 'All cities are taken'

        with lock:
            if all(city['counter'] >= city['CurrentField'] for city in cities.values()):
                return 'No available city'

        random_key = random.choice(keys)

        with lock:
            city = cities[random_key]
            if not city['taken'] and city['counter'] < city['CurrentField']:
                city['taken'] = True
                return random_key, city


def calculate_new_limit(start_field):
    # Calculate a random percentage between 2% and 5%
    percentage = random.uniform(0.02, 0.05)
    # Randomly choose to increase or decrease the limit
    if random.choice([True, False]):
        return int(start_field * (1 + percentage))
    else:
        return int(start_field * (1 - percentage))


def update_start_field(cities, config, current_interval_config):
    with lock:
        for city_id, new_value in config.items():
            if city_id in cities:
                cities[city_id]['StartField'] = current_interval_config['amountOfClicks'] * new_value
                cities[city_id]['CurrentField'] = calculate_new_limit(
                    cities[city_id]['StartField'])


def reset_cities(cities):
    with lock:
        for city in cities.values():
            city['taken'] = False
            city['counter'] = 0


def current_interval():
    now = datetime.now(timezone(timedelta(hours=3)))
    if dt_time(9, 0) <= now.time() < dt_time(17, 0):
        return '09:00-17:00'
    elif dt_time(17, 0) <= now.time() < dt_time(23, 59, 59):
        return '17:00-00:00'
    else:
        return '00:00-09:00'
