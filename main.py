# TODO: run PYTA checks
# TODO: get Djikstra to work (>:C) then integrate with vis functions
# TODO: general code review

"""
UofT Speedrunner

Module Description
==================
< description goes here >

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of the students
mentioned below and all CSC111 course staff at the University of Toronto.
Any other parties not mentioned may not use or possess copies of
this code, whether modified or otherwise.

This file is Copyright (c) 2023
Jason Barahan, Vibhas Raizada, Benjamin Sandoval, Eleonora Scognamiglio.
"""

from python_ta.contracts import check_contracts
from entities import *
from concrete_grid import *
import csv


# import the csv and read data
def load_data(building_file: str, intersection_file: str) -> AbstractGrid:
    """Load in data on all the buildings from a csv file and all the intersections from another csv file.
      This function will also create an AbstractGrid object using the buildings and intersections given, and will update
      the closest_intersection instance attribute in every building object, and the close_buildings instance attribute in
      every intersection object.

      Preconditions:
          - building_file is the path to a csv file in the format of the provided building_data.csv
          - intersection_file is the path to a csv file in the format of the provided intersection_data.csv
      """

    # loading in buildings
    with open(building_file) as building_file:
        building_reader = csv.reader(building_file)
        next(building_reader)

        buildings_dict = {}
        for row in building_reader:
            amenity_set = set()                     # handle amenities
            for i in range(4, len(row)):
                if row[i] != '':
                    amenity_set.add(row[i])

            # create a building object
            this_building = Building(row[0], row[1], amenity_set,
                                     (float(row[2]), float(row[3])))

            # associate with dictionary
            buildings_dict[row[0]] = this_building

    # loading in intersections
    with open(intersection_file) as intersection_file:
        intersection_reader = csv.reader(intersection_file, delimiter=',')
        intersections = list(intersection_reader)

        intersections_dict = {}
        for i in range(1, len(intersections)):

            # create an intersection object
            this_intersection = Intersection(
                int(intersections[i][0]),
                {intersections[i][1], intersections[i][2]},
                (float(intersections[i][3]), float(intersections[i][4])))

            # associate intersection with dictionary
            intersections_dict[int(intersections[i][0])] = this_intersection

        # TODO: need to change this with a concrete class by adding a check with if statements
        # TODO: inside a runnner function with an optional parameter that lets you choose which
        # TODO: type of concrete grid you want
        my_grid = AbstractGrid(intersections_dict, buildings_dict)
        # print(my_grid.intersections)

        # now, connect the graph
        edges_so_far = []
        for i in range(1, len(intersections)):
            row = intersections[i]
            current_intersection_id = int(row[0])

            # get adjacent intersections as stated in csv file
            for j in range(5, len(row)):
                if row[j] != '' and {current_intersection_id,
                                     int(row[j])} not in edges_so_far:
                    intersection1 = my_grid.intersections[
                        current_intersection_id]
                    intersection2 = my_grid.intersections[int(row[j])]
                    new_edge = Edge(intersection1, intersection2)

                    # update the two intersections
                    intersection1.edges.add(new_edge)
                    intersection2.edges.add(new_edge)

                    # update the accumulator
                    edges_so_far.append({current_intersection_id, int(row[j])})

    for building in my_grid.buildings:
        # print(building)
        intersection_id = my_grid.find_closest_intersection(
            my_grid.buildings[building].code)

        # print(intersection_id)
        my_grid.buildings[
            building].closest_intersection = my_grid.intersections[
                intersection_id]

    for intersection in my_grid.intersections:
        # get building codes
        buildings_code_set = my_grid.find_close_buildings(
            my_grid.intersections[intersection].identifier)
        close_buildings_set = set()

        for code in buildings_code_set:
            building_obj = my_grid.buildings[code]
            close_buildings_set.add(building_obj)
        my_grid.intersections[
            intersection].close_buildings = close_buildings_set

    return my_grid


# intersection, building, and edge is listed under entities.py

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    grid = load_data('building_data.csv', 'intersections_data.csv')

    for identifer, intersection in grid.intersections.items():
        print(identifer, [n for n in intersection.name],
              [b.name for b in intersection.close_buildings])

    # ## PythonTA checks
    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'extra-imports': [],
    #     'allowed-io': []
    # })
  
# Notes:
# load_data('building_data.csv')
# import os
# import folium
# import webbrowser
# m = folium.Map(
#     location=[43.664768, -79.390107],
#     zoom_start=50)
# # m.show_in_browser()

# filename = 'Map.html'
# m.save(filename)

# filepath = os.getcwd()
# file_uri = 'file:///' + filepath + '/' + filename
# webbrowser.open_new_tab(file_uri)
