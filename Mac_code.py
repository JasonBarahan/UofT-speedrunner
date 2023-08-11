"""This module contains the code needed to visualize and interact with a
working UI on macOS.
"""
import folium
import os
import webbrowser
import pandas as pd


# This is all default code to test
fmap = folium.Map(
        location=(43.66217731498653, -79.39539894245203),
        tiles="OpenStreetMap",
        zoom_start=15
    )

data = pd.DataFrame({
    'code': ['AB', 'AD', 'AH'],
    'name': ['Astronomy & Astrophysics', 'Enrolment Services', 'Alumni Hall'],
    'lat': [43.660427, 43.668060, 43.664768],
    'lon': [-79.397576, -79.400486, -79.390107]
}, dtype=str)

for i in range(0, len(data)):
   folium.Marker(
      location=[data.iloc[i]['lat'], data.iloc[i]['lon']],
      popup=data.iloc[i]['code'],
      tooltip=data.iloc[i]['name'],

   ).add_to(fmap)

# This code is different on macOS
filename = 'Map.html'
fmap.save(filename)

filepath = os.getcwd()
file_uri = 'file:///' + filepath + '/' + filename
webbrowser.open_new_tab(file_uri)
