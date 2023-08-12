"""
UofT Speedrunner

Module Description
==================
This module contains functions used to generate complete maps using Folium for macOS devices.
A separate map_generation_mac.py contains the corresponding code for Windows.
The completed maps include UofT buildings, intersections on campus, and paths connecting them.

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
import math

# default grid data
DEFAULT = load_all_data.load_data('data/building_data.csv', 'data/intersections_data.csv')


## Map generation tools ##
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
        name_data.sort()  # intersection name is a set
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
    Generate all intersection points with edges shown.
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


## individual point generation mechanisms for buildings and intersections ##
## these require a map to be generated                                    ##
def _generate_single_building(m: folium.Map, building: ent.Building, point: str | int, data: str = '') -> None:
    """
    Add a single building point to the given map.

    Preconditions:
    - point in {"START", "END"} or isinstance(point, int)
    """
    name = '[' + building.code + '] ' + building.name
    lat = building.coordinates[0]
    lon = building.coordinates[1]
    amenity_data = building.amenities

    # place additional context string data in brackets
    if data != '':
        data = ' (' + data + ')'

    # get amenities
    string = 'Amenities: '
    if len(amenity_data) == 0:
        string += 'None'
    else:
        for amenity in amenity_data:
            string += str(amenity) + ', '

    # modify data depending on start/end/intermediary building classifications
    if point == "START":
        icon_data = folium.Icon(color='red', icon='play', prefix='fa')
        name_data = name + data
    elif point == "END":
        icon_data = folium.Icon(color='green', icon='flag-checkered', prefix='fa')
        name_data = name + data
    elif isinstance(point, int):
        icon_data = folium.Icon(color='purple', icon='pause', prefix='fa')
        name_data = 'STOPOVER ' + str(point) + ': ' + name + data
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
                                  number: int) -> None:
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

        str2 = 'id: ', endpoint_1.identifier, points[0], 'other intersection: ', \
            endpoint_2.identifier, points[1]
        print(str2)

        # add the lines
        folium.PolyLine(points, color="red", weight=2.5, opacity=1).add_to(m)

def _visualize_intermediary_paths(m: folium.Map, edges: list[ent.Edge], intersections: list[ent.Intersection]) -> \
        list[ent.Intersection]:
    """
    Visualizes intermediary paths and their intersections.
    """
    intersections_so_far = intersections

    path_num = 2
    for edge in edges:
        latest_intersection = intersections_so_far[len(intersections_so_far) - 1]
        other_endpoint = edge.get_other_endpoint(latest_intersection)
        _generate_single_intersection(m, other_endpoint, path_num)
        intersections_so_far.append(other_endpoint)
        path_num += 1

    # map edges
    _visualize_path(m, edges)

    return intersections_so_far


def _visualize_complete_path(m: folium.Map, edges: list[list[ent.Edge]], start: ent.Building,
                             end: ent.Building, stopovers: list[ent.Building],
                             chosen_amenities: list[str]) -> None:
    """
    Visualize the shortest path between TWO buildings, utilizing a set of intersections.
    Intermediary nodes are numbered from start to end.

    Detours are optional. All detours are listed in edges[1:] in the form of a list of edges to the desired
    amenity location.

    Example:
    - start > 1 > 2 > 3 > 4 > 5
                      |
                      <-> detour 1
    """
    # generate start and end points
    _generate_single_building(m, start, 'START')
    _generate_single_building(m, end, 'END')

    # generate stopovers
    if stopovers is None or len(stopovers) == 0:
        pass
    else:
        stopover_counter = 1
        for stop in stopovers:
            # case handling when end point is listed as a stopover
            if stop == end:
                _generate_single_building(m, stop, 'END', chosen_amenities[stopover_counter - 1])
            else:
                _generate_single_building(m, stop, stopover_counter, chosen_amenities[stopover_counter - 1])
                stopover_closest_intersection_coords = stop.closest_intersection.coordinates
                points_t = [[stop.coordinates[0], stop.coordinates[1]], [stopover_closest_intersection_coords[0],
                            stopover_closest_intersection_coords[1]]]
                folium.PolyLine(points_t, color="red", weight=2.5, opacity=1).add_to(m)
            stopover_counter += 1

    # plot intersections in order
    # first intersection
    _generate_single_intersection(m, start.closest_intersection, 1)

    # map a path from start building to first intersection
    start_closest_intersection_coords = start.closest_intersection.coordinates
    points_s = [[start.coordinates[0], start.coordinates[1]],
                [start_closest_intersection_coords[0], start_closest_intersection_coords[1]]]

    folium.PolyLine(points_s, color="red", weight=2.5, opacity=1).add_to(m)

    # map a path from last intersection to destination
    end_closest_intersection_coords = end.closest_intersection.coordinates
    points_e = [[end_closest_intersection_coords[0], end_closest_intersection_coords[1]],
                [end.coordinates[0], end.coordinates[1]]]

    folium.PolyLine(points_e, color="red", weight=2.5, opacity=1).add_to(m)

    # map primary path
    intersections_in_primary_path = _visualize_intermediary_paths(m, edges[0], [start.closest_intersection])

    # map detour paths
    if len(edges[1:]) > 0:
        for path in edges[1:]:

            # handle case where no intermediary paths are required for stopovers
            if len(path) == 0:
                pass

            else:
                # we need to get the first intersection into intersections_so_far to start path generation
                add_intersection = list(path[0].endpoints)[0]
                if add_intersection not in intersections_in_primary_path:
                    add_intersection = path[0].get_other_endpoint(add_intersection)

                _visualize_intermediary_paths(m, path, [add_intersection])


# ## RUNNERS
def visualize_djikstra(start: str, end: str) -> None:
    """
    Generate and visualize a path between point A and point B.
    Note: in the final visualization of the path it is also possible for duplicates to be allowed,
    as this represent that a student may have different classes at different times and the optimal path between
    each of them may make use of an intersaction used "previously during the day".

    Preconditions:
    - start is a valid building code
    - end is a valid building code
    """
    datum = DEFAULT
    dji = load_all_data.DijkstraGrid(datum.intersections, datum.buildings)
    m = generate_map("OpenStreetMap")

    building_data = datum.buildings  # dict[str, Building]

    # start/end building data
    start_building = building_data[start]
    end_building = building_data[end]

    # start/end intersection data
    start_intersection = start_building.closest_intersection
    end_intersection = end_building.closest_intersection

    edges = dji.find_shortest_path(start_intersection.identifier, end_intersection.identifier)
    _visualize_complete_path(m, [edges], start_building, end_building, [], [])

    # output
    show_map(m)


def visualize_djikstra_with_stopovers(start: str, end: str, amenities: list[str]) -> None:
    """
    Re-implementation of Djikstra on July 10, 2023.
    Generates a path from start to end, and then generates supplementary paths that 'branch' from the initial path
    to the stopovers.

    Preconditions:
    - start is a valid building id
    - end is a valid building id
    - all elements of amenities are valid amenity strings
    """
    data = DEFAULT
    dji = load_all_data.DijkstraGrid(data.intersections, data.buildings)
    m = generate_map("OpenStreetMap")

    building_data = data.buildings  # dict[str, Building]

    # start/end building data
    start_building = building_data[start]
    end_building = building_data[end]

    # start/end intersection data
    start_intersection = start_building.closest_intersection
    end_intersection = end_building.closest_intersection

    amenity_buildings = get_buildings_by_amenity_type(amenities)
    main_path_edges = dji.find_shortest_path(start_intersection.identifier, end_intersection.identifier)
    all_paths = [main_path_edges]  # list[list[Edge]]. Begin with the main path as the first element in the list.

    # list building codes hosting amenities which are closest to main path \this is needed for generating stopovers.
    stopovers = []

    if main_path_edges:
        main_path_intersections = edge_to_intersection_path(main_path_edges)
        print(len(main_path_edges))
        print(len(main_path_intersections))
    else:
        # In this case, the path contains no edges.
        # This means that the start and end building have a common closest intersection,
        # which is used as the only "middle point" in the path
        assert building_data[start].closest_intersection == building_data[end].closest_intersection
        # At this point, we can represent the path solely as the closest intersection.
        main_path_intersections = [building_data[start].closest_intersection]

    # 1. Go through each sublist.
    # Eg: amenity_buildings = [['BN', 'GO', 'HH', 'VA', 'WS'], ['QPK', 'MUS', 'STG', 'SPD']].
    # On the first iteration, list_of_amenity_buildings = ['BN', 'GO', 'HH', 'VA', 'WS'].
    for list_of_amenity_buildings in amenity_buildings:
        amenity_id_with_shortest_distance = None
        main_intersection_id_with_shortest_distance = None
        chosen_building = None
        distance = math.inf
        # 2. Go through each individual building.
        # Eg: on the first iteration, amenity_building_code = BN.
        for amenity_building_code in list_of_amenity_buildings:
            amenity_building = building_data[amenity_building_code]
            amenity_intersection = amenity_building.closest_intersection
            amenity_id = amenity_intersection.identifier
            # 3. Go through each intersection of the main path that goes from start to end.
            for intersection in main_path_intersections:
                distance_between_main_intersection_and_amenity \
                                 = ent.get_distance(intersection.coordinates, amenity_building.coordinates)
                if distance_between_main_intersection_and_amenity < distance:
                        amenity_id_with_shortest_distance = amenity_id
                        main_intersection_id_with_shortest_distance = intersection.identifier
                        distance = distance_between_main_intersection_and_amenity
                        chosen_building = amenity_building
        optimal_path = \
            dji.find_shortest_path(main_intersection_id_with_shortest_distance, amenity_id_with_shortest_distance)
        all_paths.append(optimal_path)
        stopovers.append(chosen_building)

    _visualize_complete_path(m, all_paths, start_building, end_building, stopovers, amenities)

    # output
    show_map(m)


def get_buildings_by_amenity_type(amenities: list[str]) -> list[list[str]]:
    """Return the buildings providing the given amenities.
    In the returned list, each sublist at a given index corresponds to the buildings that provide
    the amenity listed at the same index in amenities.

    Eg. amenity_buildings = [['BN', 'GO', 'HH', 'VA', 'WS'], ['QPK', 'MUS', 'STG', 'SPD']] when
    amenities = ['gym', 'transportation'].
    """
    building_data = DEFAULT.buildings
    amenity_buildings = []
    count = 0
    for amenity in amenities:
        amenity_buildings.append([])
        for building_id in building_data:
            if amenity in building_data[building_id].amenities:
                amenity_buildings[count].append(building_id)
        count += 1

    return amenity_buildings


def edge_to_intersection_path(edges: list[ent.Edge]) -> list[ent.Intersection]:
    """Given a list of edges of a path, return the same path expressed in terms of the corresponding intersections.

    Preconditions:
     - edges != []
    """
    if len(edges) == 1:
        return list(edges[0].endpoints)
    else:
        first_endpoints = edges[0].endpoints
        second_endpoints = edges[1].endpoints
        first_intersection = list(first_endpoints.difference(second_endpoints))[0]

        # Now that we found the actual first intersection, we can iterate through the edges to find the path
        path_so_far = [first_intersection]
        for edge in edges:
            other_endpoint = edge.get_other_endpoint(path_so_far[-1])
            path_so_far.append(other_endpoint)

        return path_so_far



if __name__ == '__main__':

    a = load_all_data.load_data('data/building_data.csv', 'data/intersections_data.csv')
    generate_all_intersection_points_with_edges(a)
