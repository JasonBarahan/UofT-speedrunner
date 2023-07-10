# THIS IS A TEST FILE
# DELETE BEFORE PUSHING

import pandas as pd
import folium
import entities as ent

m = folium.Map(
       location=[43.66217731498653, -79.39539894245203],
       tiles="OpenStreetMap"
       )

# get your data
data = pd.DataFrame({
    'code': ['AB', 'AD', 'AH'],
    'name': ['Astronomy & Astrophysics', 'Enrolment Services', 'Alumni Hall'],
    'lat': [43.660427, 43.668060, 43.664768],
    'lon': [-79.397576, -79.400486, -79.390107]
}, dtype=str)

# add marker one by one on the map
for i in range(0,len(data)):
   folium.Marker(
      location=[data.iloc[i]['lat'], data.iloc[i]['lon']],
      popup=data.iloc[i]['name'],
      tooltip=data.iloc[i]['code'],

   ).add_to(m)

# get points individually
lat = [43.660427, 43.668060, 43.664768]
lon = [-79.397576, -79.400486, -79.390107]


points = []
for i in range(len(lat)):
    points.append([lat[i], lon[i]])

print(points)
# add the lines
folium.PolyLine(points, color="red", weight=2.5, opacity=1).add_to(m)

m.show_in_browser()

# Map generation tool
def generate_map(location: list(float, float), tiles: str) -> folium.Map:
    """
    Generate a Folium map object.
    """
    return folium.Map(
        location=location,
        tiles=tiles
    )


def show_map(fmap: folium.Map) -> None:
    """
    Show the Folium map object on a browser.
    """
    fmap.show_in_browser()
  

