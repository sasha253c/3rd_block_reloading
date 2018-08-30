# coding: utf-8

# # Функция interpolation() делит дистанцию trace на n РАВНЫХ отрезков

# from collections import namedtuple
from itertools import accumulate
from bisect import bisect_left

import numpy  as np
from matplotlib import pyplot as plt

import folium
from geopy.distance import great_circle
from geopy import Point

# get_ipython().run_line_magic('matplotlib', 'inline')


# In[3]:


# class Point(namedtuple('Point', ['latitude', 'longitude'])):
#     def __repr__(self):
#         return "Point(lat=%.5f, long=%.5f)" % (self.latitude, self.longitude)


# In[4]:


start = Point(51.492199, 25.761273)
SWIM = [start,
        Point(51.491758, 25.761488),
        Point(51.490893, 25.763698),
        Point(51.490666, 25.759374),
        start,
        ]
RADIUS = 6371.009  # radius Earth
BASE_POINT = (51.492309, 25.76056)

# In[5]:


SWIM


# In[6]:


def get_distance(trace):
    """Distance between of points on the trace, result in metres.
    Args:
        trace [list of Points]: List of Point(latitude, longitude)
            Example:
                [Point(51.492199, 25.761273), Point(51.491758, 25.761488),]
    Result:
        d: distance in metres
    """
    if len(trace) < 2:
        raise ValueError('Length trace must be greater then 2')

    return [great_circle(p, next_p).m for p, next_p in zip(trace, trace[1:])]


# In[7]:


def plot_trace(trace):
    plt.plot([p[0] for p in trace],
             [p[1] for p in trace], 'o--', label='swim')
    plt.grid()
    plt.legend()


# In[8]:


def map_add_circles(folium_map, trace, **kwargs):
    for point in trace:
        circle = folium.CircleMarker(point, **kwargs)
        folium_map.add_child(circle)
    return folium_map


def map_trace(trace, folium_map=None):
    if folium_map is None:
        folium_map = folium.Map(location=BASE_POINT,
                                zoom_start=14,
                                tiles="openstreetmap")
    length = len(trace)
    # add line between points on the trace
    line = folium.features.ColorLine([(p.latitude, p.longitude) for p in trace], [0, ] * (length - 1),
                                     colormap=['#3388ff', ] * (length - 1))
    folium_map.add_child(line)

    # distance
    folium_map = map_add_circles(folium_map, trace, radius=5, color='#3388ff')
    return folium_map


# In[9]:


def cartesian_transform(point):
    """Convert from Point(longitude, latitude) to Cartesian coordinates"""
    lat_rad = np.deg2rad(point.latitude)
    long_rad = np.deg2rad(point.longitude)
    x = RADIUS * np.cos(lat_rad) * np.cos(long_rad)
    y = RADIUS * np.cos(lat_rad) * np.sin(long_rad)
    z = RADIUS * np.sin(lat_rad)
    return x, y, z


def back_cartesian_transform(x, y, z):
    """ Back Convert from Cartesian coordinates to Point(longitude, latitude)"""
    return Point((np.rad2deg(np.arcsin(z / RADIUS)), np.rad2deg(np.arctan2(y, x))))


# In[10]:


def create_new_point(start, end, lambda_):
    """Находит координаты точки, которая делит отрезок между точками start и end, в соотношении lambda_,
    для этого превращае широту/долготу в 3d вектор и обратно"""
    x_start, y_start, z_start = cartesian_transform(start)
    x_end, y_end, z_end = cartesian_transform(end)
    new_x = (x_start + lambda_ * x_end) / (1 + lambda_)
    new_y = (y_start + lambda_ * y_end) / (1 + lambda_)
    new_z = (z_start + lambda_ * z_end) / (1 + lambda_)
    new_point = back_cartesian_transform(new_x, new_y, new_z)
    return new_point


# In[25]:


def interpolation(trace, n):
    """Add new points between points of the trace
    Args:
        trace [list of Points]: List of Point(latitude, longitude)
            Example:
                [Point(51.492199, 25.761273), Point(51.491758, 25.761488),]
        n [int]: разбивает участок между точками на n равных частей
    Returns:
        interpolated_trace [list of lists]: updated trace
    """
    if n < 0:
        raise ValueError("n must be greater then 0")
    # if n < len(trace)
    distance = get_distance(trace)
    accumulate_distance = list(accumulate(distance))

    new_trace = []
    for p in np.linspace(0, accumulate_distance[-1], num=n + 1)[:-1]:
        i = bisect_left(accumulate_distance, p)  # i-тому участку дистанции прегадлежит точка p
        lambda_ = great_circle(trace[i], trace[i + 1]).m / (
        accumulate_distance[i] - p) - 1  # точка p делит отрезок в соотношении lambda_
        new_point = create_new_point(trace[i], trace[i + 1], lambda_)
        new_trace.append(new_point)
    # print("%.3f (%.3f) -> %.3f [%d]" % (p, lambda_, accumulate_distance[i], i), end='; ')
    #         print("%r -> %r -> %r" % (trace[i], new_point, trace[i+1]))
    new_trace.append(trace[-1])
    return new_trace



if __name__ == '__main__':
    n = 10 * len(SWIM)
    new_trace = interpolation(SWIM, n)

    folium_map = map_trace(new_trace)
    folium_map = map_add_circles(folium_map, SWIM, radius=8, color='#ff0000')
    folium_map.save('trace.html')
