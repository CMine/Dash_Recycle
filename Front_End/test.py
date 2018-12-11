# -*- coding: utf-8 -*-
"""
Created on Fri Nov 16 11:45:05 2018

@author: kangraye
"""

import urllib.request, json, requests
import numpy as np
import copy
from boto.s3.key import Key
from boto.s3.connection import S3Connection
import boto3

#methodology from http://web.mit.edu/urban_or_book/www/book/chapter6/6.4.12.html
#https://raw.githubusercontent.com/CMine/Dash_Recycle/master/GeoJson/pickups.geojson?token=AgEbga9AZLN4f3OiMYYh4crU_oDGTKiQks5b9hyawA%3D%3D
def dash_points(URL):
    #inputs URL to get all co_ords from geoJson file
    with urllib.request.urlopen(URL) as url:
        data = json.loads(url.read().decode())
    depot = ([-73.9562, 40.7558], 0)
    co_ords = [depot]
    for feature in data['features']:
        if feature['properties']['marker-color'] == "#f95995": #pink/regular
            co_ords.append((feature['geometry']['coordinates'], 0))
        elif feature['properties']['marker-color'] == "#8867ff": #purple/morning pick-ups
            co_ords.append((feature['geometry']['coordinates'], 1))
        elif feature['properties']['marker-color'] == "#69f1eb": #blue/evening pick-ups
            co_ords.append((feature['geometry']['coordinates'],-1))
        else: #yellow/pick-ups
            co_ords.append((feature['geometry']['coordinates'], 0))
    return co_ords

def flex_points(URL):
    #inputs URL to get all co_ords from geoJson file
    with urllib.request.urlopen(URL) as url:
        data = json.loads(url.read().decode())
    depot = ([-73.9562, 40.7558], 0)
    co_ords = [depot]
    for feature in data['features']:
        if feature['properties']['marker-color'] == "#f95995": #pink/regular
            co_ords.append((feature['geometry']['coordinates'], 0))
    return co_ords

def duration_matrix(co_ords):
    #takes co-ordinate points and type and outputs a duration matrix
    URL = 'http://router.project-osrm.org/table/v1/driving/'
    for points in co_ords:
        URL += str(points[0][0]) + "," + str(points[0][1]) + ";"
    URL = URL[:-1]
    r = requests.get(url = URL)
    data = r.json()
    duration = data['durations']
    #average out to and fro time from duration matrix
    for i in range(len(duration)-1):
        for j in range(i+1, len(duration)):
            ave = 0.5*(duration[i][j] + duration[j][i])
            duration[i][j] = ave
            duration[j][i] = ave
    return duration

def load_list(co_ords,low,high):
    #takes in co-ordinates and assigns a load to them, note that there is no load at the origin
    loads = np.ceil(np.random.uniform(low-1,high,len(co_ords)))
    loads[0] = 0
    return loads

def saving_list(distance_matrix):
    #takes in similarly ordered co_ords and distance matrix and returns a sorted descending savings list, s(i,j)
    #s(i,j) = d(0,i) + d(0,j) - d(i,j)
    savings = []
    n = len(distance_matrix)
    for i in range(1, n-1):
        for j in range(i+1, n):
            if co_ords[i][1]*co_ords[j][1] >= 0:
                save = (co_ords[i][1]+co_ords[j][1])
                if save != 0:
                    save = int(save/abs(save))
                savings.append((i,j,distance_matrix[0][i]+distance_matrix[0][j]-distance_matrix[i][j],save))
    savings.sort(key=lambda tup: tup[2], reverse=True)
    return savings

def clarkWright(savings, co_ords, loads, capacity):
    #Clark Wright Algorithm for VRP problem
    capacity = capacity
    points = list(range(1,len(co_ords)))
    routes = {}

    # initiate first route
    route = [0,savings[0][0],savings[0][1],0]
    load = loads[savings[0][0]] + loads[savings[0][1]]
    routes[1] = [route, load, savings[0][3]]
    points.remove(savings[0][0])
    points.remove(savings[0][1])

    # iterate
    for i in range(1,len(savings)):
        if len(points) == 0:
            break
        point1 = savings[i][0]
        point2 = savings[i][1]
        if (point1 in points) and (point2 in points):
            route = [0,point1,point2,0]
            load = loads[point1] + loads[point2]
            routes[max([key for key in routes])+1] = [route, load, savings[i][3]]
            points.remove(point1)
            points.remove(point2)
        elif point1 in points:
            for key in routes:
                adj = [routes[key][0][1], routes[key][0][-1]]
                if point2 in adj:
                    route = copy.deepcopy(routes[key][0])
                    if point2 == adj[0]:
                        route.insert(1,point1)
                    else:
                        route.insert(-1,point1)
                    load = routes[key][1] + loads[point1]
                    label = routes[key][2]
                    if load <= capacity:
                        if label == 0:
                            routes[key] = [route, load, co_ords[point1][1]]
                            points.remove(point1)
                        elif (label == co_ords[point1][1] or co_ords[point1][1] == 0):
                            routes[key] = [route, load, label]
                            points.remove(point1)
                    break
        elif point2 in points:
            for key in routes:
                adj = [routes[key][0][1], routes[key][0][-1]]
                if point1 in adj:
                    route = copy.deepcopy(routes[key][0])
                    if point1 == adj[0]:
                        route.insert(1,point2)
                    else:
                        route.insert(-1,point2)
                    load = routes[key][1] + loads[point2]
                    label = routes[key][2]
                    if load <= capacity:
                        if label == 0:
                            routes[key] = [route, load, co_ords[point2][1]]
                            points.remove(point2)
                        elif (label == co_ords[point2][1] or co_ords[point2][1] == 0):
                            routes[key] = [route, load, label]
                            points.remove(point2)
                    break
        else:
            route1 = 0
            route2 = 0
            for key in routes:
                adj = [routes[key][0][1], routes[key][0][-1]]
                if point1 in adj:
                    if point1 == adj[0]:
                        route1 = (key, 1)
                    else:
                        route1 = (key,-1)
                if point2 in adj:
                    if point2 == adj[0]:
                        route2 = (key, 1)
                    else:
                        route2 = (key,-1)
            if route1 == 0 or route2 == 0:
                pass
            elif route1[0]!=route2[0]:
                key1 = route1[0]
                key2 = route2[0]
                load = routes[key1][1] + routes[key2][1]
                label1 = routes[key1][2]
                label2 = routes[key2][2]
                if route1[1] == -1:
                    route1 = copy.deepcopy(routes[key1][0][-2::-1])
                else:
                    route1 = copy.deepcopy(routes[key1][0][1:])
                if route2[1] == -1:
                    route2 = copy.deepcopy(routes[key2][0][-2::-1])
                else:
                    route2 = copy.deepcopy(routes[key2][0][1:])
                if load <= capacity:
                    if label1 == 0:
                        routes[key1] = [route1[::-1]+route2, load, label2]
                        del routes[key2]
                    elif label2 == 0:
                        routes[key1] = [route1[::-1]+route2, load, label1]
                        del routes[key2]
                    elif label1 == label2:
                        routes[key1] = [route1[::-1]+route2, load, label1]
                        del routes[key2]
    return routes

def distanceFromRoutes(routes, co_ords):
    #Function that checks for distance from routes
    distance = 0
    for key in routes:
        URL = 'http://router.project-osrm.org/route/v1/driving/'
        for i in range(1, len(routes[key][0])):
            URL += str(co_ords[routes[key][0][i-1]][0][0]) + "," + str(co_ords[routes[key][0][i]][0][1]) + ";"
        URL = URL[:-1]
        r = requests.get(url = URL)
        data = r.json()
        distance += data['routes'][0]["distance"]
    return distance

def routeCoords(routes, co_ords):
    #Function that outputs routes with coordinates from routes with index
    output = {}
    for key in routes:
        route = []
        for i in range(len(routes[key][0])):
            route.append(co_ords[routes[key][0][i]][0])
        output[key] = [route, routes[key][2]]
    return output

def routeToWayPoint(routes):
    #Function that takes coordinates to output waypoints
    for key in routes:
        URL = 'http://router.project-osrm.org/route/v1/driving/'
        for points in routes[key][0]:
            URL += str(points[0]) + "," + str(points[1]) + ";"
        URL = URL[:-1] + "?geometries=geojson&steps=false"
        r = requests.get(url = URL)
        data = r.json()
        routes[key][0] = data['routes'][0]['geometry']['coordinates']
    return routes

def wayPointGeoJson(routes):
    #Function to generate geojson dictionary for saving in file.
    color_key = {-1:"#69f1eb",0:"#000000",1:"#8867ff"}
    output = {"type": "FeatureCollection", "features": []}
    for key in routes:
        feature = {"type": "Feature", "geometry": {"type": "LineString", "coordinates":routes[key][0]}, \
                  "properties": {"stroke":color_key[routes[key][1]], "stroke-width":3,"stroke-opactiy":1,\
                                "name": "route" + str(key)}}
        output["features"].append(feature)
    return output

if __name__ == "__main__":
    print("Algorithm is starting")
    co_ords = dash_points("https://s3.amazonaws.com/dashrecyclegeojson/pickups.geojson")
    d_matrix = duration_matrix(co_ords)
    loads = load_list(co_ords,0,4)
    savings = saving_list(d_matrix)
    routes = clarkWright(savings, co_ords, loads, 25)
    print("Calculating the distance matrix")
    distance = distanceFromRoutes(routes, co_ords)
    routes = routeCoords(routes, co_ords)
    routes = routeToWayPoint(routes)
    print("Preparing to write to the S3 bucket")
    AWS_ACCESS_KEY_ID = 'AKIAIOJANDUTPP2YZ5PA'
    AWS_SECRET_ACCESS_KEY = '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'

    bucket_name = "dashrecyclegeojson"
    updated_filename = "routes.geojson"
    s3 = boto3.client("s3", aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    s3.put_object(Body=json.dumps(wayPointGeoJson(routes)), Bucket="dashrecyclegeojson", Key=updated_filename, ACL='public-read')
    print("Write to S3 bucket is complete")
