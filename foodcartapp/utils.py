from django.core.cache import cache
from geopy.distance import distance
import requests


def fetch_coordinates(apikey, place):
    base_url = 'https://geocode-maps.yandex.ru/1.x'
    params = {'geocode': place, 'apikey': apikey, 'format': 'json'}
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    places_found = response.json()['response']['GeoObjectCollection']['featureMember']
    if not places_found:
        return None, None
    most_relevant = places_found[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(' ')
    return float(lat), float(lon)


def get_restaurant_distance(apikey, order_address, restaurant_address):
    all_coords = []
    for address in (order_address, restaurant_address):
        coords = cache.get(address)
        if coords:
            all_coords.append(coords)
            continue
        coords = fetch_coordinates(apikey, address)
        cache.set(address, coords, None)
        all_coords.append(coords)

    return round(distance(*all_coords).kilometers, 3)
