import datetime
import os
import pandas as pd
import numpy as np
import googlemaps

from pymongo import MongoClient
from math import radians, cos, sin, asin, sqrt
from bson.son import SON


MONGO_URL = os.environ["mongo_server"] # Dirección mlab para la base de datos
GMAPS_APIKEY = os.environ["gmaps_api_key"]

client = MongoClient(MONGO_URL)
gmaps = googlemaps.Client(key=GMAPS_APIKEY)

db = client.datalab
locations = db.locations

def get_near_documents(longitude,latitude):
    max_distance = 0
    objects = 0
    while objects <= 10:
        max_distance = max_distance + 1000
        query = {'geopoint': {
        '$near': SON([('$geometry', SON([
            ('type', 'Point'),
            ('coordinates', [longitude, latitude])])),
            ('$maxDistance', max_distance)])}}
        response =list(locations.find(query))
        objects = len(response)
    return response


def list_geopoint_extract(place_list):
    geopoint = place_list["geopoint"]
    longitude = geopoint["coordinates"][0]
    latitude = geopoint["coordinates"][1]
    return longitude, latitude


def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    m = 6367000 * c
    return m


def coords_stringify(longitude,latitude):
    output = str(latitude) + ","+ str(longitude)
    return output


def get_directions(longitude1, latitude1, longitude2, latitude2, route_type):
    try:
        dir1string = coords_stringify(longitude1, latitude1)
        dir2string= coords_stringify(longitude2, latitude2)
        directions_result = gmaps.directions(dir1string,dir2string, mode=route_type, departure_time= datetime.datetime.now())
        distance = directions_result[0]["legs"][0]["distance"]["value"]
        route = directions_result[0]["legs"][0]["steps"]
    except:
        distance = np.nan
        route = np.nan
    return distance, route

def route_distance_info(row,longitude1, latitude1, route_type):
    longitude2, latitude2 = list_geopoint_extract(row)
    if route_type == "euclidean":
        distance = haversine(longitude1, latitude1, longitude2, latitude2)
        route = np.nan
    elif route_type == "walking":
        distance, route = get_directions(longitude1, latitude1, longitude2, latitude2, "walking")
    else:
        distance, route = get_directions(longitude1, latitude1, longitude2, latitude2, "driving")
    return distance, route


def directions_row(row, longitude1, latitude1, route_type):
    row["distance"], row["route"] = route_distance_info(row,longitude1, latitude1, route_type)
    return row


def find_nearest_top(longitude, latitude, mode, head):
    near_places = get_near_documents(longitude, latitude)
    dataframe_places = pd.DataFrame(near_places)
    dataframe_distances= dataframe_places.apply(directions_row,  axis=1, args = (longitude, latitude, mode))
    if mode is not "euclidean":
        dataframe_distances = dataframe_distances.dropna()
    df_distances_top = dataframe_distances.head(head)
    return df_distances_top

def nearest_response(longitude, latitude, mode, head):
    response_df = find_nearest_top(longitude, latitude, mode, head)
    response_dict = response_df.to_dict(orient="records")
    return(response_dict)
