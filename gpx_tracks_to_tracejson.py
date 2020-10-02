# coding: utf-8
### nlehuby - gpx > geojson (tracejson) for bus routes

import gpxpy
import geojson

def gpx_to_geojson(gpx):
    #TODO (needs to be refined, there are lots of other cases to handle)
    stops_crowdness = ["vide", "mi-plein", "plein", "surchargé"]
    stop_waypoints = ["abribus", "arrêt sans indication","poteau"]

    features = []
    metadata = {}

    metadata["duration"] = round(gpx.get_duration()/60)
    metadata["distance"] = (gpx.length_2d() / 1000)


    for waypoint in gpx.waypoints:
        if waypoint.name.startswith('Départ'):
            metadata["raw_departure"] = waypoint.name
        elif waypoint.name.startswith('Terminus') or waypoint.name.startswith('Arrivé') or waypoint.name.startswith('descente'):
            metadata["raw_arrival"] = waypoint.name
        elif waypoint.name in stop_waypoints:
            try:
                features[-1]["properties"]["equipments"] = waypoint.name
            except IndexError:
                continue 
        elif waypoint.name in stops_crowdness:
            try:
                features[-1]["properties"]["crowdness"] = waypoint.name
            except IndexError:
                continue        
        else :
            geom = geojson.Point([waypoint.longitude, waypoint.latitude])
            props = {"name" : waypoint.name}
            props["timestamps"] = [ int(waypoint.time.timestamp()) ] 
            stop_feature = geojson.Feature(geometry=geom, properties= props)
            features.append(stop_feature)

    metadata["stops_number"] = len(features)   
    
    shape = []
    metadata["timestamps"] = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                shape.append([point.longitude, point.latitude])
                metadata["timestamps"].append(int(point.time.timestamp()))

    features.append( geojson.Feature(geometry=geojson.LineString(shape), 
                                    properties=metadata) )
    
    return geojson.FeatureCollection(features)


def gpx_to_geojson_file(gpx, output_file_name):
    feature_collection = gpx_to_geojson(gpx)
    with open(output_file_name, 'w') as f:
        geojson.dump(feature_collection, f, indent = 6)


if __name__ == '__main__':

    with open("./Lien vers 2017-10-31_20-06-03.gpx", "r") as gpx_file:
        gpx = gpxpy.parse(gpx_file)
        geojson_ = gpx_to_geojson(gpx)


