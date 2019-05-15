# coding: utf-8
### nlehuby - AccraMobile3

import os
import requests
import gpxpy
import json

# Find close ways thanks to overpass

def coords_to_overpass_query(coord_list):
    """ transform a list of coord to an overpass query for highways around
    """
    overpass_query = "(around:20"
    for point in coord_list:
        overpass_query += ",{},{}".format(point['lat'],point['lon'])
    overpass_query += ")"
    full_overpass_request = "[out:xml][timeout:250];(way[highway]{};);out meta;>;out meta qt;".format(overpass_query)
    return full_overpass_request

if __name__ == '__main__':
    gpx_shape = []

    with open("./Lien vers 2017-10-31_20-06-03.gpx", "r") as gpx_file:
        gpx = gpxpy.parse(gpx_file)

        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    coord = {}
                    coord["lon"] = point.longitude
                    coord["lat"] = point.latitude
                    gpx_shape.append(coord)

    print(coords_to_overpass_query(gpx_shape))
