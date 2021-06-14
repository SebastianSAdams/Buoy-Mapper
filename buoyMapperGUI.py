# -*- coding: utf-8 -*-
"""
Created on Mon May 31 23:22:47 2021

@author: sebas
"""

import tkinter as tk
import warnings
from IPython import get_ipython
from datetime import datetime
import pdb
from buoyMapper import (apiGet, calcDriftSpeed, placeDayVector, placeHourVector,
                        pd, Point, gpd, plt, make_axes_locatable)

#10/31/2020-1:24:00AM -b 11/4/2020-6:54:00PM

def startDateAction(value):
    global START_DATE
    START_DATE = datetime.strptime(value, '%m/%d/%Y-%I:%M:%S%p')
    START_DATE = START_DATE.isoformat()
    return START_DATE

def endDateAction(value):
    global END_DATE
    END_DATE = datetime.strptime(value, '%m/%d/%Y-%I:%M:%S%p')
    END_DATE = END_DATE.isoformat()
    return END_DATE

def runBuoyMapper():

    print('start runBuoyMapper')
    get_ipython().run_line_magic('matplotlib', 'qt')

    lakeMap = gpd.read_file('./hydro_p_LakeSuperior/hydro_p_LakeSuperior.shp')

    API_KEY = '9b5b0e8377a2805157c883a7f9d7b3'
    if apiKey.get() != '':
        API_KEY = apiKey.get()

    START_DATE = ''
    if startDate.get() != '':
        START_DATE = startDateAction(startDate.get())

    END_DATE = ''
    if endDate.get() != '':
        END_DATE = endDateAction(endDate.get())

    spotterId = spotID.get()

    data = apiGet(API_KEY, spotterId, START_DATE, END_DATE)

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
    print('end runBuoyMapper')

print('start GUI')
root = tk.Tk()
root.title('Buoy Mapper')

canvas = tk.Canvas(root, height=700, width=1200)
canvas.pack()

frame = tk.Frame(root, bg='light green')
frame.place(relx=0, rely=0, relwidth=1, relheight=1)

title = tk.Label(root, text='Buoy Mapper', font=('Courier', 35), bg='light green')
title.place(relx=.3, rely=0.01, relwidth=.4, relheight=.08)

spotID = tk.Entry(frame, justify='center')
spotID.place(relx=.1825, rely=.2, relwidth=.3, relheight=.047)
spotLabel = tk.Label(frame, text = 'Spotter ID:')
spotLabel.place(relx=.1, rely=.2, relwidth=.0825, relheight=.047)
endFormatLabel = tk.Label(frame, text = "i.e. 'SPOT-1234'",
                          bg = 'light green')
endFormatLabel.place(relx=.1825, rely=.248, relwidth=.3, relheight=.017)


startDate = tk.Entry(frame, justify='center')
startDate.place(relx=.1825, rely=.3, relwidth=.3, relheight=.047)
startDateLabel = tk.Label(frame, text = 'Data Start Date:')
startDateLabel.place(relx=.1, rely=.3, relwidth=.0825, relheight=.047)
startFormatLabel = tk.Label(frame, text = "'MM/DD/YYYY-H:MM:SSAM' (or PM)",
                          bg = 'light green')
startFormatLabel.place(relx=.1825, rely=.348, relwidth=.3, relheight=.017)


endDate = tk.Entry(frame, justify='center')
endDate.place(relx=.1825, rely=.4, relwidth=.3, relheight=.047)
endDateLabel = tk.Label(frame, text = 'Data End Date:')
endDateLabel.place(relx=.1, rely=.4, relwidth=.0825, relheight=.047)
endFormatLabel = tk.Label(frame, text = "'MM/DD/YYYY-H:MM:SSAM' (or PM)",
                          bg = 'light green')
endFormatLabel.place(relx=.1825, rely=.448, relwidth=.3, relheight=.017)


apiKey = tk.Entry(frame, justify='center')
apiKey.place(relx=.1825, rely=.5, relwidth=.3, relheight=.047)
keyLabel = tk.Label(frame, text = 'API Auth Token:')
keyLabel.place(relx=.1, rely=.5, relwidth=.0825, relheight=.047)


button = tk.Button(frame, text='Run', command = lambda: runBuoyMapper()) 
button.place(relx=.75, rely=.87, relwidth=.2, relheight=.05)

version = tk.Label(frame, text='Version 1.0', bg='light green')
version.place(relx=0.94, rely=0.94)

name = tk.Label(frame, text='Sebastian Adams', bg='light green')
name.place(relx=0.914, rely=0.965)

root.mainloop()