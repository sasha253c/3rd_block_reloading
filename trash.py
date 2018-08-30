import folium
from folium.plugins import TimestampedGeoJson

tgs = TimestampedGeoJson({
    'type': 'FeatureCollection',
    'features': [
      {
        'type': 'Feature',
        'geometry': {
          'type': 'LineString',
          'coordinates': [[25.76068639755249, 51.491778257971646],[25.76020359992981, 51.494289892197],[25.763508081436157, 51.49448360291841]],
          },
        'properties': {
          'times': [1435708800000, 1435795200000, 1435881600000]
          }
        }
      ]
    }, duration='PT1S')


# folium_map = folium.Map(location=(51.492309, 25.76056),
#                         zoom_start=14,
#                         tiles="openstreetmap")
# folium_map.add_child(tgs)
# folium_map.save('trace_trash.html')
print(folium.__version__)
marker = folium.Marker()