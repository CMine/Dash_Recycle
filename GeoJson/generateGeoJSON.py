#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 13 10:43:55 2018

@author: Cammie
"""
from geojson import Point, Feature, FeatureCollection, dump
import tempfile
import numpy as np

# Read in the customer names and convert them to points
def loadNames(path):
    nameFile = open(path, "r")
    names = [name for name in nameFile]
    return names
        

# Read in the coordinates and convert them to points
def loadCoordinates(path):
    coordinates = open(path, "r")
    locations = []
    for coord in coordinates:
        features = coord.split(",")
        lon_lat = (float(features[3]),float(features[1]))
        locations.append(Point(lon_lat))
    return locations

# Use the points, name, and desired color to build the feature
def buildFeatures(points, names, color):
    features = []
    for point, name in zip(points, names):
        features.append(Feature(geometry=point, 
                                properties={"name": name, 
                                "marker-color": color,
                                "marker-symbol": "waste-basket",
                                "line": "blue"}))
    return features

# Dump the features into a GEOJSON file
def writeToGeoJSON(filename, features):
    feature_collection = FeatureCollection(features)
    with open(filename, 'w') as f:
        dump(feature_collection, f)


        


if __name__ == "__main__":
    # Load coordinates
    coords = loadCoordinates("/Users/Cammie/Desktop/coords.txt")
    
    # Load names
    names = loadNames("/Users/Cammie/Desktop/names.txt")
    
    # Partition coords and name to build features 
    original_featues = buildFeatures(coords[0:25], names[0:25], "#f95995")    
    single_features = buildFeatures(coords[25:35], names[25:35], "#8867ff")
    double_features = buildFeatures(coords[35:45], names[35:45], "#69f1eb")
    long_features = buildFeatures(coords[45:50], names[45:50], "#efbd50")
    
    # Concatenate all the features
    all_features = original_featues + single_features + double_features + long_features

    # Write data to file
    writeToGeoJSON("pickups.geojson", all_features)                                  
                                  
                                  
    
