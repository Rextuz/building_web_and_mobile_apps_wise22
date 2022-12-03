import functools
import json
from pathlib import Path

import folium
import requests
import pandas as pd
from geopy import Nominatim
from geopy.distance import geodesic


def cache(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        cache_dir = Path("cache")
        cache_dir.mkdir(exist_ok=True)
        cache_file = Path(cache_dir, f"{f.__name__}_cache.json")
        if not cache_file.exists():
            json.dump({}, cache_file.open("w"))
        cache_file.touch(exist_ok=True)
        existing_cache = json.load(cache_file.open())
        key = "--->".join(str(arg) for arg in args)
        if key not in existing_cache:
            result = f(*args, **kwargs)
            existing_cache[key] = result
        json.dump(existing_cache, cache_file.open("w"), indent=2)
        return existing_cache[key]
    return wrapper


def create_map(coords_list, lat_lons):
    m = folium.Map()
    df = pd.DataFrame()
    # add markers for the places we visit
    for point in lat_lons:
        folium.Marker(point).add_to(m)
    # loop over the responses and plot the lines of the route
    for coords in coords_list:
        points = [(i[1], i[0]) for i in coords]

        # add the lines
        folium.PolyLine(points, weight=5, opacity=1).add_to(m)
        temp = pd.DataFrame(coords).rename(columns={0: "Lon", 1: "Lat"})[
            ["Lat", "Lon"]
        ]
        df = pd.concat([df, temp])
    # create optimal zoom
    sw = df[["Lat", "Lon"]].min().values.tolist()
    sw = [sw[0] - 0.0005, sw[1] - 0.0005]
    ne = df[["Lat", "Lon"]].max().values.tolist()
    ne = [ne[0] + 0.0005, ne[1] + 0.0005]
    m.fit_bounds([sw, ne])
    return m


@cache
def get_coords(lat1, long1, lat2, long2, mode="drive"):
    url = "https://route-and-directions.p.rapidapi.com/v1/routing"
    try:
        key = open("rapidapi_token.txt").read().strip()
    except FileNotFoundError:
        print("No API token found. Get one from https://rapidapi.com/geoapify-gmbh-geoapify/api/route-and-directions/")
        return
    host = "route-and-directions.p.rapidapi.com"
    headers = {"X-RapidAPI-Key": key, "X-RapidAPI-Host": host}
    querystring = {
        "waypoints": f"{str(lat1)},{str(long1)}|{str(lat2)},{str(long2)}",
        "mode": mode,
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    coordinates = response.json()["features"][0]["geometry"]["coordinates"][0]
    return coordinates


@cache
def get_lat_long_from_address(address):
    locator = Nominatim(user_agent="myGeocoder")
    location = locator.geocode(address)
    return location.latitude, location.longitude


@cache
def distance(address0, address1):
    coord0 = get_lat_long_from_address(address0)
    coord1 = get_lat_long_from_address(address1)
    return geodesic(coord0, coord1).miles


def sort(*waypoints, target):
    address_to_distance = {}
    for waypoint in set(waypoints):
        address_to_distance[waypoint] = distance(waypoint, target)
    sorted_addresses = dict(sorted(address_to_distance.items(), key=lambda x: x[1]))
    return list(sorted_addresses.keys())


def get_map(addresses):
    lat_lons = [get_lat_long_from_address(addr) for addr in addresses]
    coords_list = []
    for n in range(len(lat_lons) - 1):
        lat1, lon1, lat2, lon2 = (
            lat_lons[n][0],
            lat_lons[n][1],
            lat_lons[n + 1][0],
            lat_lons[n + 1][1],
        )
        coords = get_coords(
            lat1, lon1, lat2, lon2, mode="drive"
        )
        coords_list.append(coords)
    return create_map(coords_list, lat_lons)
