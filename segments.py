# coding: utf-8

# Function create_segments() divides trace on *N* equal segments.

import pathlib
from itertools import accumulate
from bisect import bisect_left

import folium
import numpy  as np
from geopy.distance import great_circle
from geopy import Point

from distance import START, SWIM, RADIUS, map_add_trace, map_add_circles


def get_distance(trace):
    """Distance between of points on the trace, result in metres.
    Args:
        trace [list of Points]: List of Point(latitude, longitude)
            Example:
                [Point(51.492199, 25.761273), Point(51.491758, 25.761488),]
    Returns:
        Distance in metres
    """
    if len(trace) < 2:
        raise ValueError('Length trace must be greater then 2')

    return [great_circle(p, next_p).m for p, next_p in zip(trace, trace[1:])]


def cartesian_transform(point):
    """Convert from Point(longitude, latitude) to Cartesian coordinates"""
    lat_rad = np.deg2rad(point.latitude)
    long_rad = np.deg2rad(point.longitude)
    x = RADIUS * np.cos(lat_rad) * np.cos(long_rad)
    y = RADIUS * np.cos(lat_rad) * np.sin(long_rad)
    z = RADIUS * np.sin(lat_rad)
    return x, y, z


def back_cartesian_transform(x, y, z):
    """ Back convert from Cartesian coordinates to Point(longitude, latitude)"""
    return Point((np.rad2deg(np.arcsin(z / RADIUS)), np.rad2deg(np.arctan2(y, x))))


def create_new_point(start, end, lambda_):
    """Находит координаты точки, которая делит отрезок между точками start и end, в соотношении lambda_, для этого превращает широту/долготу в 3d вектор и обратно"""
    x_start, y_start, z_start = cartesian_transform(start)
    x_end, y_end, z_end = cartesian_transform(end)
    new_x = (x_start + lambda_ * x_end) / (1 + lambda_)
    new_y = (y_start + lambda_ * y_end) / (1 + lambda_)
    new_z = (z_start + lambda_ * z_end) / (1 + lambda_)
    new_point = back_cartesian_transform(new_x, new_y, new_z)
    return new_point


def create_segments(trace, n):
    """Trace segmentation, divide trace on n equal segments.
    Args:
        trace (list/tuple of Points): List/Tuple of Point(latitude, longitude)
            Example:
                [Point(51.492199, 25.761273), Point(51.491758, 25.761488),];

        n (int): count of segments.

    Returns:
        new_trace [list of Points]: new trace with equal segments.
    """
    if n <= 1:
        raise ValueError("n must be greater then 1.")
    distance = get_distance(trace)
    accumulate_distance = list(accumulate(distance))

    new_trace = []
    for p in np.linspace(0, accumulate_distance[-1], num=n + 1)[:-1]:
        i = bisect_left(accumulate_distance, p)  # i-тому участку дистанции прегадлежит точка p
        lambda_ = great_circle(trace[i], trace[i + 1]).m / (accumulate_distance[i] - p) - 1  # точка p делит отрезок в соотношении lambda_
        new_point = create_new_point(trace[i], trace[i + 1], lambda_)
        new_trace.append(new_point)
    # print("%.3f (%.3f) -> %.3f [%d]" % (p, lambda_, accumulate_distance[i], i), end='; ')
    #         print("%r -> %r -> %r" % (trace[i], new_point, trace[i+1]))
    new_trace.append(trace[-1])
    return new_trace


if __name__ == '__main__':
    n = 10 * len(SWIM)
    new_trace = create_segments([START, ] + SWIM + [START, ], n)

    folium_map = folium.Map(location=(START.latitude, START.longitude),
                            zoom_start=14,
                            tiles="openstreetmap")
    folium_map = map_add_trace(folium_map, new_trace)
    folium_map = map_add_circles(folium_map, SWIM, radius=8, color='#ff0000')
    folium_map.save(str(pathlib.Path.cwd().joinpath('map', 'trace.html')))
