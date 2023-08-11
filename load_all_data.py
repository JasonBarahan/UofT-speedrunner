"""
UofT Speedrunner

Module Description
==================
This module contains the function needed to read and process our datasets: building_data.csv and intersection_data.csv.
It also creates a full grid from the files.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of the students
mentioned below and all CSC111 course staff at the University of Toronto.
Any other parties not mentioned may not use or possess copies of
this code, whether modified or otherwise.

This file is Copyright (c) 2023
Jason Barahan, Vibhas Raizada, Benjamin Sandoval, Eleonora Scognamiglio.
"""
import csv
from entities import *
from concrete_grid import *


# import the csv and read data
def load_data(building_file: str, intersection_file: str) -> AbstractGrid:
    """
    Load in data on all the buildings from data/building_data.csv and all the intersections from
    data/interasection_data.csv.
    This function will also create an AbstractGrid object using the buildings and intersections given, and will update
    the closest_intersection instance attribute in every building object, and the close_buildings instance attribute
    in every intersection object according to the datasets provided.

    Preconditions:
      - building_file is the path to a csv file in the format of the provided building_data.csv
      - intersection_file is the path to a csv file in the format of the provided intersection_data.csv
    """
    # loading in buildings
    buildings_dict = load_buildings(building_file)

    # loading in intersections
    intersections, intersections_dict = load_intersections(intersection_file)

    my_grid = AbstractGrid(intersections_dict, buildings_dict)

    # now, connect the graph
    edges_so_far = []
    for i in range(1, len(intersections)):
        row = intersections[i]
        current_intersection_id = int(row[0])
        for j in range(5, len(row)):
            if row[j] != '' and {current_intersection_id, int(row[j])} not in edges_so_far:
                intersection1 = my_grid.intersections[current_intersection_id]
                intersection2 = my_grid.intersections[int(row[j])]
                new_edge = Edge(intersection1, intersection2)
                # update the two intersections
                intersection1.edges.add(new_edge)
                intersection2.edges.add(new_edge)
                # update the accumulator
                edges_so_far.append({current_intersection_id, int(row[j])})

    join_buildings_intersections(my_grid)

    return my_grid


def load_buildings(building_file: str) -> dict[str, Building]:
    """Helper method to load in buildings as objects from building file, and save buildings as a dict
    with the key: value form of building's code: building's object

    Preconditions:
        - building_file is the path to a csv file in the format of the provided building_data.csv
    """
    with open(building_file) as imported_building_file:
        building_reader = csv.reader(imported_building_file)
        next(building_reader)

        buildings_dict = {}
        for row in building_reader:
            amenity_set = set()
            for i in range(4, len(row)):
                if row[i] != '':
                    amenity_set.add(row[i])
            this_building = Building(row[0], row[1], amenity_set,
                                     (float(row[2]), float(row[3])))
            buildings_dict[row[0]] = this_building
    return buildings_dict


def load_intersections(intersection_file: str) -> tuple[list, dict[int, Intersection]]:
    """Helper method to load in intersections as objects from intersections file, and save intersections as a dict
    with the key: value form of intersection's integer id: intersection's object;
    Return a list from our intersection rows from the intersection file

    Preconditions:
        - intersection_file is the path to a csv file in the format of the provided intersection_data.csv"""
    with open(intersection_file) as imported_intersection_file:
        intersection_reader = csv.reader(imported_intersection_file, delimiter=',')
        intersections = list(intersection_reader)

        intersections_dict = {}
        for i in range(1, len(intersections)):
            this_intersection = Intersection(int(intersections[i][0]), {intersections[i][1], intersections[i][2]},
                                             (float(intersections[i][3]), float(intersections[i][4])))
            intersections_dict[int(intersections[i][0])] = this_intersection

    return intersections, intersections_dict


def join_buildings_intersections(my_grid: AbstractGrid) -> None:
    """Helper method that mutates grid to connect buildings with closest intersections."""
    for building in my_grid.buildings:
        intersection_id = my_grid.find_closest_intersection(my_grid.buildings[building].code)
        my_grid.buildings[building].closest_intersection = my_grid.intersections[
            intersection_id]

    for intersection_obj in my_grid.intersections:
        buildings_code_set = my_grid.find_close_buildings(my_grid.intersections[intersection_obj].identifier)
        close_buildings_set = set()
        for code in buildings_code_set:
            building_obj = my_grid.buildings[code]
            close_buildings_set.add(building_obj)
        my_grid.intersections[intersection_obj].close_buildings = close_buildings_set


if __name__ == '__main__':
    import doctest

    doctest.testmod()
