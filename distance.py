# coding: utf-8

# # Drawing all distance of the 3rd Block. Reloading.

import pathlib
import sys


import numpy as np
import folium
from geopy import Point
from PIL import Image


START = Point(51.49228, 25.76123)
SWIM = [Point(51.491758, 25.761488),
        Point(51.490893, 25.763698),
        Point(51.490666, 25.759374),
        ]

TRANSIT_ZONE_IN = Point(51.4926, 25.76125)
TRANSIT_ZONE_OUT = Point(51.4929, 25.76114)
TURN_BACK_BIKE = Point(51.53540, 25.66007)
TURN_BACK_RUN = Point(51.48977, 25.73769)
FINISH = Point(51.49244, 25.76091)

RADIUS = 6371.009  # Earth radius
ICONS_PATH = pathlib.Path.cwd().joinpath('icons')

# One WAY

bike_one_way = [
    Point(51.49337, 25.76091),
    Point(51.49346, 25.76154),
    Point(51.49382, 25.76186),
    Point(51.49425, 25.76207),
    Point(51.49438, 25.76203),
    Point(51.49451, 25.76347),
    Point(51.50641, 25.74924),
    Point(51.50709, 25.74529),
    Point(51.51499, 25.73543),
    Point(51.51840, 25.72922),
    Point(51.52304, 25.71184),
    Point(51.52426, 25.70951),
    Point(51.52590, 25.70302),
    Point(51.52364, 25.69098),
    Point(51.52584, 25.67270),
    Point(51.52625, 25.67129),
    Point(51.52975, 25.66838),
    Point(51.53157, 25.66594),
    Point(51.53371, 25.66538),
    Point(51.53419, 25.66463),
    TURN_BACK_BIKE,

]

BIKE = bike_one_way + bike_one_way[::-1]


RUN = [
    Point(51.49306, 25.76102),
    Point(51.49317, 25.76046),
    Point(51.49318, 25.76011),
    Point(51.49388, 25.75987),
    Point(51.49387, 25.75813),
    Point(51.49428, 25.75776),
    Point(51.49426, 25.75685),
    Point(51.49309, 25.75622),
    Point(51.49255, 25.75553),
    Point(51.49176, 25.75256),
    Point(51.49166, 25.75023),
    Point(51.49168, 25.74894),
    Point(51.49222, 25.74718),
    Point(51.49313, 25.74406),
    Point(51.49292, 25.74187),
    Point(51.49222, 25.73933),
    Point(51.49235, 25.73801),
    Point(51.49180, 25.73786),
    Point(51.49149, 25.73745),
    Point(51.49146, 25.73680),
    Point(51.49044, 25.73595),
    # back
    TURN_BACK_RUN,
    Point(51.49044, 25.73595),
    Point(51.49146, 25.7368),
    Point(51.49149, 25.73745),
    Point(51.4918, 25.73786),
    Point(51.49235, 25.73801),
    Point(51.49222, 25.73933),
    Point(51.49292, 25.74187),
    Point(51.49313, 25.74406),
    Point(51.49222, 25.74718),
    Point(51.49168, 25.74894),
    Point(51.49166, 25.75023),
    Point(51.49162, 25.75184),
    Point(51.49104, 25.75310),
    Point(51.49077, 25.75467),
    Point(51.49129, 25.75702),
    Point(51.49125, 25.75721),
    Point(51.49211, 25.76054),
    Point(51.49235, 25.76046),
]

TOTAL_DISTANCE = [START, ] + SWIM + [START, TRANSIT_ZONE_IN, TRANSIT_ZONE_OUT] + BIKE + [TRANSIT_ZONE_IN,
                                                                                         TRANSIT_ZONE_OUT] + RUN + [
                     FINISH, ]



def create_marker(folium_map, point, image_path, popup=''):
    """Add marker to folium.Map with a custom icon"""
    image = Image.open(image_path)
    icon = folium.features.CustomIcon(np.array(image))
    marker = folium.Marker(point, popup=popup, icon=icon)
    return folium_map.add_child(marker)


def map_add_circles(folium_map, trace, **kwargs):
    for point in trace:
        circle = folium.CircleMarker(point, **kwargs)
        folium_map.add_child(circle)
    return folium_map

def map_add_trace(folium_map, trace):
    length = len(trace)
    # add line between points on the trace
    line = folium.features.ColorLine([(p.latitude, p.longitude) for p in trace], [0, ] * (length - 1),
                                     colormap=['#3388ff', ] * (length - 1))
    folium_map.add_child(line)

    # distance
    folium_map = map_add_circles(folium_map, trace, radius=5, color='#3388ff')
    return folium_map


## Drawing all Distance
if __name__ == '__main__':
    folium_map = folium.Map(location=(START.latitude, START.longitude),
                            zoom_start=13,
                            tiles="openstreetmap")

    # create Icons
    start_image_path = ICONS_PATH.joinpath("start.png")
    transit_image_path = ICONS_PATH.joinpath("transit.png")
    finish_image_path = ICONS_PATH.joinpath("finish.png")
    turn_back_bike_image_path = ICONS_PATH.joinpath("turn_back_bike.png")
    turn_back_run_image_path = ICONS_PATH.joinpath("turn_back_run.png")

    for point, path_icon, popup in ((START, start_image_path, 'Start'),
                                    (TRANSIT_ZONE_IN, transit_image_path, 'TRANSIT_ZONE_IN'),
                                    (TRANSIT_ZONE_OUT, transit_image_path, 'TRANSIT_ZONE_OUT'),
                                    (TURN_BACK_BIKE, turn_back_bike_image_path, 'TURN_BACK_BIKE'),
                                    (TURN_BACK_RUN, turn_back_run_image_path, 'TURN_BACK_RUN'),
                                    (FINISH, finish_image_path, 'FINISH'),
                                    ):
        folium_map = create_marker(folium_map, point=point, image_path=path_icon, popup=popup)

    folium_map = map_add_circles(folium_map, SWIM, radius=8, color='#ff0000')
    folium_map = map_add_trace(folium_map, TOTAL_DISTANCE)
    folium_map.save(str(pathlib.Path.cwd().joinpath('map', 'distance.html')))

