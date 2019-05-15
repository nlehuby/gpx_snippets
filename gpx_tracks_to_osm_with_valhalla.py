# coding: utf-8
### nlehuby - AccraMobile3

import os
import requests
import gpxpy
import json

# Mapmatch with valhalla
default_trace_route_url = "https://valhalla.mapzen.com/trace_route?api_key=mapzen-jLrDBSP&"
default_trace_attributes_url = "https://valhalla.mapzen.com/trace_attributes?api_key=mapzen-jLrDBSP&"
trace_route_url = os.getenv('valhalla_trace_route_url', default_trace_route_url)
trace_attributes_url = os.getenv('valhalla_trace_attributes_url', default_trace_route_url)

def geojson_to_text(a_geojson):
    """ transform a geojson in a txt parameter that you can send to valhalla
    """
    shape = []
    for a_couple in a_geojson['geometry']['coordinates']:
        coord = {}
        coord["lon"] = a_couple[0]
        coord["lat"] = a_couple[1]
        shape.append(coord)
    shape_txt = str(shape)
    shape_txt = shape_txt.replace("'","\"")
    return shape_txt

def decode(encoded):
    """ decode an encoded string """
    #six degrees of precision in valhalla
    inv = 1.0 / 1e6;
    decoded = []
    previous = [0,0]
    i = 0
    #for each byte
    while i < len(encoded):
        #for each coord (lat, lon)
        ll = [0,0]
        for j in [0, 1]:
          shift = 0
          byte = 0x20
          #keep decoding bytes until you have this coord
          while byte >= 0x20:
            byte = ord(encoded[i]) - 63
            i += 1
            ll[j] |= (byte & 0x1f) << shift
            shift += 5
          #get the final value adding the previous offset and remember it for the next
          ll[j] = previous[j] + (~(ll[j] >> 1) if ll[j] & 1 else (ll[j] >> 1))
          previous[j] = ll[j]
    #scale by the precision and chop off long coords also flip the positions so
    #its the far more standard lon,lat instead of lat,lon
    #decoded.append([float('%.6f' % (ll[1] * inv)), float('%.6f' % (ll[0] * inv))])
        decoded.append({"lon": float('%.6f' % (ll[1] * inv)), "lat": float('%.6f' % (ll[0] * inv))})
    #hand back the list of coordinates
    return decoded

def from_shape_to_way_list(coord):
    # step 1 - trace_attributes
    data = '{"shape":'+ coord +',"costing":"auto","directions_options":{"units":"miles"},"shape_match":"map_snap"}'
    ta1 = requests.post(trace_attributes_url,  data = data)

    output = ta1.json()
    if 'error' in output:
        print ('trace_attributes error : {}'.format(output['error']))
        return
    output_polyline = output["shape"]

    #step 2 - trace_route
    shape_2_txt = str(decode(output_polyline))
    shape_2_txt = shape_2_txt.replace("'","\"")
    trace_route_data = '{"shape":'+ shape_2_txt +',"costing":"auto","directions_options":{"units":"miles"},"shape_match":"map_snap"}'

    tr = requests.post(trace_route_url,  data = trace_route_data)
    output = tr.json()
    if 'error' in output:
        print ('trace_route error : {}'.format(output['error']))
        return
    output_polyline2 = output['trip']['legs'][0]['shape']

    #step 3 - trace_attributes again
    shape_3_txt = str(decode(output_polyline2))
    shape_3_txt = shape_3_txt.replace("'","\"")
    trace_attributes_data = '{"shape":'+ shape_3_txt +',"costing":"auto","directions_options":{"units":"miles"},"shape_match":"map_snap"}'

    ta = requests.post(trace_attributes_url,  data = trace_attributes_data)
    output = ta.json()
    if 'error' in output:
        print ('trace_attributes again error : {}'.format(output['error']))
        return

    #output
    osm_way_list=[]
    for a_way in output['edges']:
        osm_way_list.append('w' + str(a_way['way_id']))
    return osm_way_list



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
    shape_txt = str(gpx_shape)
    shape_txt = shape_txt.replace("'","\"")
    tt = from_shape_to_way_list(shape_txt)

    if tt is not None:
        josm_link = "http://localhost:8111/load_object?objects="
        josm_link += ','.join(tt)

    print(josm_link)
