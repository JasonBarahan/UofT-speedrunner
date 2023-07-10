# TODO: run PYTA checks
# TODO: get Djikstra to work (>:C) then integrate with vis functions
# TODO: general code review

"""
UofT Speedrunner

Module Description
==================
This module contains functions used to generate complete maps using Folium.
Completed maps include UofT buildings, intersections on campus, and paths connecting
the two.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of the students
mentioned below and all CSC111 course staff at the University of Toronto.
No other person shall have access to code within this file, whether
original or modified. Violators shall be sent to Mars.

This file is Copyright (c) 2023
Jason Barahan, Vibhas Raizada, Benjamin Sandoval, Eleonora Scognamiglio.
Special thanks to OpenStreetMaps for providing the map tile data.
"""
import folium
import entities as ent
import load_all_data
import os
import webbrowser

# default grid data
DEFAULT = load_all_data.load_data('building_data.csv', 'intersections_data.csv')


# ## Map generation tools ##
def generate_map(tiles: str, location: list[float] = (43.66217731498653, -79.39539894245203)) -> folium.Map:
    """
    Generate a Folium map object centered at the University of Toronto.
    """
    return folium.Map(
        location=location,
        tiles=tiles,
        zoom_start=15
    )


def show_map(fmap: folium.Map) -> None:
    """
    Show the Folium map object on a browser.
    """
    filename = 'Map.html'
    fmap.save(filename)

    filepath = os.getcwd()
    file_uri = 'file:///' + filepath + '/' + filename
    webbrowser.open_new_tab(file_uri)


# ## general map generation mechanisms for buildings and intersections ##
def generate_all_building_points(amenity: str = None, grid: ent.AbstractGrid = DEFAULT) -> None:
    """
    Visualize all buildings which have a specified amenity, or all buildings if amenity is None.

    Preconditions:
    - (amenity in ent.AMENITIES) or (amenity is None)
    """
    data = grid.buildings
    names = []
    lat = []
    lon = []
    amenities = []

    for i in [j for j in data if (amenity in data[j].amenities) or (amenity is None)]:
        # get list of all building names
        str3 = '[' + i + '] ' + data[i].name
        names.append(str3)

        # get amenities
        amenity_data = list(data[i].amenities)
        print(amenity_data)
        if len(amenity_data) == 0:
            amenities.append('')
        else:
            string = 'Amenities: '
            for amenity in amenity_data:
                string += str(amenity) + ', '
            amenities.append(string)

        # get coordinates
        lat.append(data[i].coordinates[0])
        lon.append(data[i].coordinates[1])

    # generate map object
    m = generate_map("OpenStreetMap")

    # add marker one by one on the map
    assert len(lat) == len(lon) == len(amenities) == len(names)
    for j in range(len(lat)):
        folium.Marker(
            location=[lat[j], lon[j]],
            popup=amenities[j],
            tooltip=names[j],
            icon=folium.Icon(color='cadetblue', icon='building', prefix='fa')
        ).add_to(m)

    show_map(m)


def generate_all_intersection_points(grid: ent.AbstractGrid = DEFAULT) -> None:
    """
    Generate all intersections extant in the intersection data file.
    """
    data = grid.intersections
    names = []
    lat = []
    lon = []

    # get ids
    ids = [i for i in data]

    for i in range(1, len(data) + 1):
        # get names
        name_data = list(data[i].name)
        name_data.sort()                         # intersection name is a set
        if len(name_data) < 2:
            name_data.append(name_data[0])
        st = name_data[0] + ' @ ' + name_data[1]
        names.append(st)

        # get coordinates
        lat.append(data[i].coordinates[0])
        lon.append(data[i].coordinates[1])

    # generate map object
    m = generate_map("OpenStreetMap")

    # add marker one by one on the map
    assert len(lat) == len(lon) == len(names) == len(ids)

    for i in range(0, len(lat)):
        folium.Marker(
            location=[lat[i], lon[i]],
            popup=names[i],
            tooltip=ids[i],
            icon=folium.Icon(color='gray', icon='traffic-light', prefix='fa')
        ).add_to(m)

    show_map(m)


def generate_all_intersection_points_with_edges(grid: ent.AbstractGrid = DEFAULT,
                                                ids: list[int] = None) -> None:
    """
    Generate all intersection points with edges shown
    """
    data = grid.intersections
    names = []
    lat = []
    lon = []

    if ids is None:     # default behaviour
        ids = [i for i in grid.intersections]

    # get ids
    for i in ids:
        # get names
        name_data = list(data[i].name)
        name_data.sort()                         # intersection name is a set
        if len(name_data) < 2:
            name_data.append(name_data[0])
        st = name_data[0] + ' @ ' + name_data[1]
        names.append(st)

        # get coordinates
        lat.append(data[i].coordinates[0])
        lon.append(data[i].coordinates[1])

    # generate map object
    m = generate_map("OpenStreetMap")

    # add marker one by one on the map
    assert len(lat) == len(lon) == len(names) == len(ids)

    for i in range(0, len(lat)):
        folium.Marker(
            location=[lat[i], lon[i]],
            popup=names[i],
            tooltip=ids[i],
            icon=folium.Icon(color='gray', icon='traffic-light', prefix='fa')
        ).add_to(m)

    for i in ids:
        edges_to_examine = list(data[i].edges)
        print(edges_to_examine)
        _visualize_path(m, edges_to_examine)

    show_map(m)


# ## individual point generation mechanisms for buildings and intersections ##
# ## these require a map to be generated                                    ##
def _generate_single_building(m: folium.Map, building: ent.Building, point: str | int) -> None:
    """
    Add a single building point to the given map.

    Preconditions:
    - point in {"START", "END"} or isinstance(point, int)
    """
    name = '[' + building.code + '] ' + building.name
    lat = building.coordinates[0]
    lon = building.coordinates[1]
    amenity_data = building.amenities

    # get amenities
    print(amenity_data)             # TODO: debug
    string = 'Amenities: '
    if len(amenity_data) == 0:
        string += 'None'
    else:
        for amenity in amenity_data:
            string += str(amenity) + ', '

    # modify data depending on start/end/intermediary building classifications
    if point == "START":
        icon_data = folium.Icon(color='red', icon='play', prefix='fa')
        name_data = name
    elif point == "END":
        icon_data = folium.Icon(color='green', icon='flag-checkered', prefix='fa')
        name_data = name
    elif isinstance(point, int):
        icon_data = folium.Icon(color='purple', icon='pause', prefix='fa')
        name_data = 'STOPOVER ' + str(point) + ': ' + name
    else:
        raise Exception("You found a bug! Send us a message and we'll give you a cookie in exchange.")

    # add marker
    folium.Marker(
        location=[lat, lon],
        popup=string,
        tooltip=name_data,
        icon=icon_data
    ).add_to(m)


def _generate_single_intersection(m: folium.Map, intersection: ent.Intersection,
                                  number: int):
    """
    Add a single intersection to the given map.

    Preconditions:
    - int > 0
    """
    lat = intersection.coordinates[0]
    lon = intersection.coordinates[1]

    # get names
    name_data = list(intersection.name)
    name_data.sort()  # intersection name is a set
    if len(name_data) < 2:          # handle single named intersection
        name_data.append(name_data[0])
    names = '[' + str(number) + '] ' + name_data[0] + ' @ ' + name_data[1]

    # add marker
    folium.Marker(
        location=[lat, lon],
        # popup=names,
        # tooltip=str(id),
        tooltip=names,
        icon=folium.Icon(color='gray', icon='traffic-light', prefix='fa')
    ).add_to(m)


# path generation tools
def _visualize_path(m: folium.Map, edges: list[ent.Edge]) -> None:
    """
    Visualize paths between two nodes given a list of edges.
    """
    # for each edge, get the coordinates for each endpoint
    for edge in edges:
        # getting endpoints
        endpoint_1 = list(edge.endpoints)[0]
        endpoint_2 = edge.get_other_endpoint(endpoint_1)

        # getting the coordinates
        points = [[endpoint_1.coordinates[0], endpoint_1.coordinates[1]],
                  [endpoint_2.coordinates[0], endpoint_2.coordinates[1]]]

        # TODO: remove debug
        str2 = 'id: ', endpoint_1.identifier, points[0], 'other intersection: ', \
            endpoint_2.identifier, points[1]
        print(str2)

        # add the lines
        folium.PolyLine(points, color="red", weight=2.5, opacity=1).add_to(m)


def _visualize_complete_path(m: folium.Map, edges: list[ent.Edge], start: ent.Building,
                            end: ent.Building, intermediate_stops: list[ent.Building] | None = None) -> None:
    """
    Visualize the shortest path between TWO buildings, utilizing a set of intersections.
    Intermediary nodes are numbered from start to end.

    Detours are optional.

    Example:
    - start > 1 > 2 > 3 > 4 > 5
    """
    intersections_so_far = []

    # generate start and end points
    _generate_single_building(m, start, 'START')
    _generate_single_building(m, end, 'END')

    # generate intermediate points
    if intermediate_stops is None:
        pass
    else:
        c = 1
        for stop in intermediate_stops:
            _generate_single_building(m, stop, c)
            c += 1

    # plot intersections in order
    # # first intersection
    _generate_single_intersection(m, start.closest_intersection, 1)
    intersections_so_far.append(start.closest_intersection)

    # # intermediary intersections and final intersection
    # - get other endpoint
    num = 2
    for edge in edges:
        latest_intersection = intersections_so_far[len(intersections_so_far) - 1]
        other_endpoint = edge.get_other_endpoint(latest_intersection)
        _generate_single_intersection(m, other_endpoint, num)
        intersections_so_far.append(other_endpoint)
        num += 1

    # map a path from start building to first intersection
    start_closest_intersection_coords = start.closest_intersection.coordinates
    points_s = [[start.coordinates[0], start.coordinates[1]],
                [start_closest_intersection_coords[0], start_closest_intersection_coords[1]]]

    folium.PolyLine(points_s, color="red", weight=2.5, opacity=1).add_to(m)

    # map edges
    _visualize_path(m, edges)

    # map a path from last intersection to destination
    end_closest_intersection_coords = end.closest_intersection.coordinates
    points_e = [[end_closest_intersection_coords[0], end_closest_intersection_coords[1]],
                [end.coordinates[0], end.coordinates[1]]]

    folium.PolyLine(points_e, color="red", weight=2.5, opacity=1).add_to(m)

    # map paths to intermediate buildings
    if intermediate_stops is None:
        pass
    else:
        for stop in intermediate_stops:
            intm_closest_intersection_coords = stop.closest_intersection.coordinates
            points_m = [[intm_closest_intersection_coords[0], intm_closest_intersection_coords[1]],
                        [stop.coordinates[0], stop.coordinates[1]]]

            folium.PolyLine(points_m, color="red", weight=2.5, opacity=1).add_to(m)


# ## RUNNERS
def visualize_dfs(start: str, end: str, intermediate_stops: list[str]) -> None:
    """
    Generate a path between point A and point B, and all intermediate stops, if needed, using depth-first search.
    Note: this always assumes the user wants to go to intermediate stops in a specific order (non-flexible).
    Note: it is also possible for duplicates to be allowed (different classes at different times)

    Preconditions:
    - start is a valid building code
    - end is a valid building code
    - all elements of intermediate_stops are valid building codes
    """
    datum = load_all_data.load_data('building_data.csv', 'intersections_data.csv')
    dfs = load_all_data.DFSGrid(datum.intersections, datum.buildings)
    m = generate_map("OpenStreetMap")

    building_data = datum.buildings

    # start/end building data
    start_building = building_data[start]
    end_building = building_data[end]

    # start/end intersection data
    start_intersection = start_building.closest_intersection
    end_intersection = end_building.closest_intersection

    # handle intermediate stops
    detour_buildings = [building_data[a] for a in intermediate_stops]
    detour_close_intersection_ids = [b.closest_intersection.identifier for b in detour_buildings]

    # generate path, increasing the max distance depending on number of stopovers
    max_distance = max(len(detour_buildings) * 500 + 2000, 3500)
    edges = dfs.find_shortest_path(start_intersection.identifier, end_intersection.identifier,
                                   set(detour_close_intersection_ids), max_distance)
    _visualize_complete_path(m, edges, start_building, end_building, detour_buildings)

    # output
    show_map(m)


def visualize_djikstra(start: str, end: str) -> None:
    """
    Generate a path between point A and point B, and all intermediate stops, if needed.
    Note: this always assumes the user wants to go to intermediate stops in a specific order (non-flexible).
    Note: it is also possible for duplicates to be allowed (different classes at different times)

    Preconditions:
    - start is a valid building code
    - end is a valid building code
    - all elements of intermediate_stops are valid building codes
    """
    datum = load_all_data.load_data('building_data.csv', 'intersections_data.csv')
    dji = load_all_data.DijkstraGrid(datum.intersections, datum.buildings)
    m = generate_map("OpenStreetMap")

    building_data = datum.buildings

    # start/end building data
    start_building = building_data[start]
    end_building = building_data[end]

    # start/end intersection data
    start_intersection = start_building.closest_intersection
    end_intersection = end_building.closest_intersection

    # generate path, increasing the max distance depending on number of stopovers
    # max_distance = len(detour_buildings) * 1000 + 2000
    # max_distance = 3500

    edges = dji.find_shortest_path(start_intersection.identifier, end_intersection.identifier)
    _visualize_complete_path(m, edges, start_building, end_building)

    # output
    show_map(m)


if __name__ == '__main__':
    # ## PythonTA checks
    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'extra-imports': [],
    #     'allowed-io': []
    # })

    a = load_all_data.load_data('building_data.csv', 'intersections_data.csv')
    generate_all_intersection_points_with_edges(a)
    # generate_all_building_points(a)

    # start2 = 'MY'
    # end2 = 'WB'
    # detours2 = []
    #
    # runner_dfs(start2, end2, detours2)
    # runner_djikstra(start2, end2, detours2)