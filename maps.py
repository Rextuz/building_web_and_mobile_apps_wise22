import folium
import requests
import pandas as pd
from geopy import Nominatim


def create_map(responses, lat_lons):
    m = folium.Map()
    df = pd.DataFrame()
    # add markers for the places we visit
    for point in lat_lons:
        folium.Marker(point).add_to(m)
    # loop over the responses and plot the lines of the route
    for response in responses:
        mls = response.json()["features"][0]["geometry"]["coordinates"]
        points = [(i[1], i[0]) for i in mls[0]]

        # add the lines
        folium.PolyLine(points, weight=5, opacity=1).add_to(m)
        temp = pd.DataFrame(mls[0]).rename(columns={0: "Lon", 1: "Lat"})[["Lat", "Lon"]]
        df = pd.concat([df, temp])
    # create optimal zoom
    sw = df[["Lat", "Lon"]].min().values.tolist()
    sw = [sw[0] - 0.0005, sw[1] - 0.0005]
    ne = df[["Lat", "Lon"]].max().values.tolist()
    ne = [ne[0] + 0.0005, ne[1] + 0.0005]
    m.fit_bounds([sw, ne])
    return m


def get_directions_response(lat1, long1, lat2, long2, mode="drive"):
    url = "https://route-and-directions.p.rapidapi.com/v1/routing"
    key = (
        open("rapidapi_token.txt").read().strip()
    )  # https://rapidapi.com/geoapify-gmbh-geoapify/api/route-and-directions/
    host = "route-and-directions.p.rapidapi.com"
    headers = {"X-RapidAPI-Key": key, "X-RapidAPI-Host": host}
    querystring = {
        "waypoints": f"{str(lat1)},{str(long1)}|{str(lat2)},{str(long2)}",
        "mode": mode,
    }
    return requests.request("GET", url, headers=headers, params=querystring)


def get_lat_long_from_address(address):
    locator = Nominatim(user_agent="myGeocoder")
    location = locator.geocode(address)
    return location.latitude, location.longitude


def get_map(addresses):
    lat_lons = [get_lat_long_from_address(addr) for addr in addresses]
    responses = []
    for n in range(len(lat_lons) - 1):
        lat1, lon1, lat2, lon2 = (
            lat_lons[n][0],
            lat_lons[n][1],
            lat_lons[n + 1][0],
            lat_lons[n + 1][1],
        )
        response = get_directions_response(lat1, lon1, lat2, lon2, mode="drive")
        responses.append(response)
    return create_map(responses, lat_lons)
