#! python
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 18:21:35 2021

@author: sebas
"""

from math import radians, cos, sin, atan2, degrees
from haversine import haversine
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
from IPython import get_ipython
from mpl_toolkits.axes_grid1 import make_axes_locatable
import math
from statistics import mean
import requests
import dateutil.parser
from datetime import datetime
import warnings
import argparse
import os.path
from os import path

global API_KEY
global START_DATE
global END_DATE
global API_TOKEN_FNAME
API_TOKEN_FNAME = './apiKey.TXT'
API_KEY = ''
'9b5b0e8377a2805157c883a7f9d7b3'
SPOTTER_ID = 'SPOT-0592'
START_DATE = ''
'20201031T012400-0400'
END_DATE = ''
'20201104T185400-0400'
'20201031T085400-0500'

def getHaversine(lat1, long1, lat2, long2):
    # Returns the displacement in meters between two lat/long pairs, accounting
    # for curvature of the Earth using the Haversine formula

    displacement = haversine((lat1, long1), (lat2, long2), unit='m')
    return displacement

def getBearing(lat1, long1, lat2, long2):
    # Returns the compass bearing from the first lat/long pair to the second
    # pair

    lat1 = radians(lat1)
    lat2 = radians(lat2)
    long1 = radians(long1)
    long2 = radians(long2)

    bearing = atan2(sin(long2-long1)*cos(lat2),
                    cos(lat1)*sin(lat2)-sin(lat1)*cos(lat2)*cos(long2-long1))

    bearing = degrees(bearing)
    bearing = (bearing + 360) % 360
    return bearing

def placeVector(df, ax, file):

    a = [df.at[(df['longitude'].shape[0]-2), 'longitude'],
         df.at[(df['latitude'].shape[0]-2), 'latitude']]
    b = [df.at[(df['longitude'].shape[0]-1), 'longitude'],
         df.at[(df['latitude'].shape[0]-1), 'latitude']]

    head_length = .001

    dx = b[0] - a[0]
    dy = b[1] - a[1]

    vec_ab = [dx,dy]
    
    vec_ab_magnitude = math.sqrt(dx**2+dy**2)

    dx = dx / vec_ab_magnitude
    dy = dy / vec_ab_magnitude

    ax.arrow(a[0], a[1], vec_ab_magnitude*dx*20, vec_ab_magnitude*dy*20,
             head_width=0.0005, head_length=head_length, width=0.0000001,
             fc='red', ec='black')

    plt.scatter(a[0],a[1],color='black')
    plt.scatter(b[0],b[1],color='black')


def placeHourVector(df, ax):

    a = [df.at[(df['longitude'].shape[0]-1), 'longitude'],
         df.at[(df['latitude'].shape[0]-1), 'latitude']]

    b = [df.at[(df['longitude'].shape[0]-2), 'longitude'],
         df.at[(df['latitude'].shape[0]-2), 'latitude']]

    c = [df.at[(df['longitude'].shape[0]-3), 'longitude'],
         df.at[(df['latitude'].shape[0]-3), 'latitude']]

    avgx = (a[0] + b[0] + c[0]) / 3
    avgy = (a[1] + b[1] + c[1]) / 3

    dx = a[0] - avgx
    dy = a[1] - avgy

    vec_ab = [dx,dy]

    vec_ab_magnitude = math.sqrt(dx**2+dy**2)

    head_length = vec_ab_magnitude * 0.25

    dx = dx / vec_ab_magnitude
    dy = dy / vec_ab_magnitude

    ax.arrow(a[0], a[1], vec_ab_magnitude*dx, vec_ab_magnitude*dy,
             head_width=head_length*0.35, length_includes_head = True,
             head_length=head_length, width=0.0000001, fc='red', ec='black')

    endPtLabel = (round(a[0]+vec_ab_magnitude*dx, 3), round(a[1]+vec_ab_magnitude*dy, 3))

    ax.annotate(endPtLabel,
                (a[0]-vec_ab_magnitude*dx, a[1]+vec_ab_magnitude*dy),
                fontsize=10)


def placeDayVector(df, ax):

    xList = []
    yList = []

    a = [df.at[(df['longitude'].shape[0]-1), 'longitude'],
         df.at[(df['latitude'].shape[0]-1), 'latitude']]

    for i in range(len(df['longitude'])-47, len(df['longitude'])+1):
        dif = df.at[(df['longitude'].shape[0]-i+1, 'longitude')] - df.at[(df['longitude'].shape[0]-i, 'longitude')]
        xList.append(dif)
        i=i+1

    for i in range(len(df['latitude'])-47, len(df['latitude'])+1):
        dif = df.at[(df['latitude'].shape[0]-i+1, 'latitude')] - df.at[(df['latitude'].shape[0]-i, 'latitude')]
        yList.append(dif)
        i=i+1

    avgx = mean(xList)
    avgy = mean(yList)
    print(avgx, avgy)

    dx = avgx
    dy = avgy

    vec_ab = [dx,dy]

    vec_ab_magnitude = math.sqrt(dx**2+dy**2)

    head_length = vec_ab_magnitude * 0.25

    dx = dx / vec_ab_magnitude
    dy = dy / vec_ab_magnitude

    ax.arrow(a[0], a[1], vec_ab_magnitude*dx, vec_ab_magnitude*dy,
             head_width=head_length*0.35, length_includes_head = True,
             head_length=head_length, width=0.0000001, fc='yellow', ec='black')

    endPtLabel = (round(a[0]+vec_ab_magnitude*dx, 3), round(a[1]+vec_ab_magnitude*dy, 3))

    ax.annotate(endPtLabel,
                (a[0]+vec_ab_magnitude*dx, a[1]+vec_ab_magnitude*dy),
                fontsize=10)

def apiGet(apiKey, spotID, startDate, endDate):

    params = {
        'token': apiKey,
        'spotterId':spotID,
        'startDate':startDate,
        'endDate':endDate
        }
    response = requests.get(
        url='https://api.sofarocean.com/api/wave-data',
        params=params)
    data = response.json()
    return data

def calcDriftSpeed(data, lat, long):
    driftSpeed = []
    timedif = []
    z = 0
    for i in data['data']['waves']:
        if z == 0:
            z += 1
        else:
            date = dateutil.parser.parse(data['data']['waves'][z]['timestamp'])
            date2 = dateutil.parser.parse(data['data']['waves'][z-1]['timestamp'])
            z += 1
            dif = date-date2
            timedif.append(dif.seconds)
    z = 0
    for j in long:
        if z == 0:
            z += 1
        else:
            d = getHaversine(lat[z-1], long[z-1], lat[z], long[z])
            speed = d / timedif[z-1]
            speedDictionary = {"driftSpeed" : speed}
            data['data']['waves'][z].update(speedDictionary)
            driftSpeed.append(speed)
            z += 1
    return data

class startDateAction(argparse.Action):
    def __call__(self, parser, args, values, option_string=None):
        global START_DATE
        START_DATE = datetime.strptime(values, '%m/%d/%Y-%I:%M:%S%p')
        START_DATE = START_DATE.isoformat()

class endDateAction(argparse.Action):
    def __call__(self, parser, args, values, option_string=None):
        global END_DATE
        END_DATE = datetime.strptime(values, '%m/%d/%Y-%I:%M:%S%p')
        END_DATE = END_DATE.isoformat()

def getApiKey():
    global API_TOKEN_FNAME
    if not path.exists(API_TOKEN_FNAME):
        return None
    if not path.isfile(API_TOKEN_FNAME):
        return None
    with open(API_TOKEN_FNAME, 'r') as file:
        apiToken = file.read()
        if len(apiToken) == 0:
            return None

    return apiToken

def main():

    lakeMap = gpd.read_file('./hydro_p_LakeSuperior/hydro_p_LakeSuperior.shp')

    aParser = argparse.ArgumentParser(description='Displays buoy location' +
                                      ' and speed data from given range')

    aParser.add_argument('-s', '--spotterid', required=True,
                         metavar='spotter-id',
                         help='Spotter buoy ID (i.e. SPOT-1234)')

    aParser.add_argument('-a', '--startdate', required=False,
                         metavar='data-start-date', action = startDateAction,
                         help='Start date of data range')

    aParser.add_argument('-b', '--enddate', required=False,
                         metavar='data-end-date', action = endDateAction,
                         help='End date of data range')

    aParser.add_argument('-k', '--apikey', required=False,
                         metavar='api-key',
                         help='API authentication key')

    args = aParser.parse_args()
    global API_KEY
    global START_DATE
    global END_DATE
    global API_TOKEN_FNAME

    if args.apikey is not None:
        API_KEY = args.apikey
    else:
        API_KEY = getApiKey()
        if API_KEY is None:
            warnings.warn("An API key was not provided either in the input" +
                          " field or in the API key file {}.".format(API_TOKEN_FNAME))
            raise SystemExit(1)

    data = apiGet(API_KEY, args.spotterid, START_DATE, END_DATE)

    z = 0
    longitude = []
    for i in data['data']['waves']:
        longitude.append(data['data']['waves'][z]['longitude']) 
        z += 1

    z = 0
    latitude = []
    for i in data['data']['waves']:
        latitude.append(data['data']['waves'][z]['latitude']) 
        z += 1

    calcDriftSpeed(data, latitude, longitude)

    df = pd.DataFrame(data['data']['waves'])

    geometry = [Point(xy) for xy in zip(longitude, latitude)]
    #geometry[:3]

    geodf = gpd.GeoDataFrame(df, crs = 4326, geometry = geometry)
    geodf.head() # might not be necessary

    fig,ax = plt.subplots(figsize = (15,15))
    lakeMap.plot(ax = ax, label = 'Buoy Position')

    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='5%', pad=0.1)

    geodf.plot(ax = ax, cax=cax, cmap = 'Oranges',
               markersize = 60, marker = 's', label = 'Buoy Position',
               column = "driftSpeed", legend=True,
               legend_kwds={'label': 'Buoy Speed (m/s)'})
    ax.legend()
    ax.set_title('Spotter Buoy Location and Speed')

    try:
        placeHourVector(geodf, ax)
    except KeyError:
        warnings.warn("Not enough data to calculate predictive vector based on past 1 hour of data")

    try:
        placeDayVector(geodf, ax)
    except KeyError:
        warnings.warn("Not enough data to calculate predictive vector based on past 24 hours of data")

    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')

    plt.legend(prop={'size':15})

    print('end')

if __name__ == '__main__':
    main()
else:
    print('main failed')