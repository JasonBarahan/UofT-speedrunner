"""
UofT Speedrunner

Module Description
==================
This file contains entities used to build a meaningful graph in our problem domain.
The entities we used are: Building, Intersection, Edge and AbstractGrid, parent class of the different
concrete grids (see concrete_grid.py).
The Intersections are the nodes in the graph we are using to represent our enhanced UofT map, and they are
connected by Edges, which represent the segment of street connecting two intersections.
Important UofT buildings are also featured on the map.
AbstractGrid is an object used to represent the graph as a whole, and is the main "map" object, which can be
further used to find nearby buildings from a given intersection, and shortest paths between two buildings.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of the students
mentioned below and all CSC111 course staff at the University of Toronto.
Any other parties not mentioned may not use or possess copies of
this code, whether modified or otherwise.

This file is Copyright (c) 2023.
Jason Barahan, Vibhas Raizada, Benjamin Sandoval, Eleonora Scognamiglio.
"""
from __future__ import annotations
from typing import Optional
import math

# Global variables
AMENITIES = {
    'study', 'dining', 'coffee', 'microwave', 'gym', 'library', 'atm',
    'math learning centre', 'writing centre', 'transportation'
}


class Building:
    """
    A class for the buildings within the UofT campus.

    Instance Attributes:
      - code: a string containing a two-letter unique building
        identifier
      - closest_intersection: the Intersection closest to the building's
        main entrance
      - amenities: a list of strings specifying amenities available in the building.
      - coordinates: a tuple consisting of (longitude, latitude)

    Representation Invariants:
      - self.code is a valid building code
      - all(a in AMENITIES for a in self.amenities)
      - self.closest_interaction is None or any(self.coordinates == b.coordinates
        for b in self.closest_intersection.close_buildings)
    """
    code: str
    name: str
    closest_intersection: Optional[Intersection]
    amenities: set[str]
    coordinates: tuple[float, float]

    def __init__(self, code: str, name: str, amenities: set[str],
                 coordinates: tuple[float, float]) -> None:
        """Initialize all attributes BUT the closest intersection. This is because
        we will calculate the closest intersection when we import the CSVs."""
        self.code = code
        self.name = name
        self.closest_intersection = None
        self.amenities = amenities
        self.coordinates = coordinates


class Intersection:
    """
    A class for the intersections (nodes) within the UofT campus.
    Each Intersection object represent a relevant intersection between two or more streets on the UofT campus.

      Instance Attributes:
      - identifier: intersection id
      - name: a set of strings intersecting at this point
      - close_buildings: a set of buildings closest to this intersections
      - coordinates: a tuple consisting of (longitude, latitude)
      - edges: edges connected to this intersection

      Representation Invariants:
       - self.close_buildings == set() or all(self.coordinates == b.closest_intersection.coordinates
        for b in self.close_buildings)
      """
    identifier: int
    name: set[str]
    close_buildings: set[Building]
    coordinates: tuple[float, float]
    edges: set[Edge]

    def __init__(self, identifier: int, name: set[str],
                 coordinates: tuple[float, float]) -> None:
        """
        Initialize an intersection object.

        Note:
        - close_buildings is initialized EMPTY as we are determining the close buildings after-the-fact.
        - edges is EMPTY as adjacent intersections will be determined after-the-fact.
        """
        self.identifier = identifier
        self.name = name
        self.close_buildings = set()  # empty
        self.coordinates = coordinates
        self.edges = set()  # edges are empty

    def find_all_paths(self, destination_id: int, visited: set[Intersection],
                       max_distance: int) -> list[list[Edge]]:
        """
        Finds all the paths from self to destination_id.
        When you call this method for the first time, destination_id is the id of the node you want to get to and
        visited should be an empty set.
        """

        all_paths_so_far = []
        self._find_all_paths_helper(destination_id, visited, [],
                                    all_paths_so_far, max_distance)
        return all_paths_so_far

    def _find_all_paths_helper(self, destination_id: int,
                               visited: set[Intersection],
                               path_so_far: list[Edge],
                               all_paths_so_far: list[list[Edge]],
                               max_distance: int) -> None:
        """Helper to find_all_paths"""

        if self.identifier == destination_id:
            all_paths_so_far.append(path_so_far)
        else:
            visited.add(self)

            for edge in self.edges:
                neighbour = edge.get_other_endpoint(self)
                new_path_so_far = path_so_far.copy()
                new_path_so_far.append(edge)

                sum_so_far = sum(e.distance for e in new_path_so_far)

                if neighbour not in visited and sum_so_far < max_distance:
                    # Critical that a copy is passed into the recursive call.
                    # Otherwise, the same visited set will be mutated and affect other recursive branches.
                    # Same goes for a copy of path_so_far.
                    neighbour._find_all_paths_helper(destination_id,
                                                     visited.copy(),
                                                     new_path_so_far,
                                                     all_paths_so_far,
                                                     max_distance)

    def find_edge(self, other_intersection: Intersection) -> Optional[Edge]:
        """Find the edge between self and other_intersection.

        Preconditions:
          - self and other_intersections are connected
        """
        for edge in self.edges:
            if edge.get_other_endpoint(self).identifier == other_intersection.identifier:
                return edge
        return None  # this should never be reached


class Edge:
    """
      The 'roadway' connecting two Intersections. Each edge represents the segment of a given street
      connecting the two Intersections, which act as its endpoints in the graph representation.
      Edges are weighted by the real-life distance between Intersections.

      Instance Attributes:
      - endpoints: the Intersections an edge connects
      - distance: the length of the Edge; the distance between endpoints

      Representation Invariants:
      - len(endpoints) == 2
      """
    endpoints: set[Intersection]
    distance: float

    def __init__(self, intersection1: Intersection,
                 intersection2: Intersection) -> None:
        """
        Initialize an edge object representing a connection between two nodes
        (intersection or building). Edges are weighted to measure distance between.
        """
        self.endpoints = {intersection1, intersection2}
        distance = get_distance(intersection1.coordinates,
                                intersection2.coordinates)
        self.distance = distance

    def get_other_endpoint(self, intersection: Intersection) -> Intersection:
        """Return the endpoint of this Edge that is not equal to the given intersection.

        Preconditions:
            - intersection in self.endpoints
        """
        return (self.endpoints - {intersection}).pop()


class AbstractGrid:
    """
    An abstract class representing the map of UofT.
    It brings together all intersections as nodes, and buildings as features located on the map.

    Instance Attributes:
    - intersections: dict of intersections (key: intersection ID. value: Intersection object)
    - buildings: dict of buildings (key: building code. value: Building object)
    """
    intersections: dict[int, Intersection]
    buildings: dict[str, Building]

    def __init__(self, intersections: dict[int, Intersection],
                 buildings: dict[str, Building]) -> None:
        """Initialize an Abstract Grid object, representing a map of the U of T campus"""
        self.intersections = intersections
        self.buildings = buildings

    def find_closest_intersection(self, building_code: str) -> int:
        """Finds and returns the ID of the intersection with the closest Euclidean distance to that of the building
        of the given building code. Used for the initialization of all buildings.
        """
        closest_so_far = None
        closest_distance = None
        for identifier, intersection in self.intersections.items():
            if closest_so_far is None:
                closest_so_far = identifier
                coordinates1 = intersection.coordinates
                coordinates2 = self.buildings[building_code].coordinates
                closest_distance = get_distance(coordinates1, coordinates2)
            else:
                coordinates1 = intersection.coordinates
                coordinates2 = self.buildings[building_code].coordinates
                distance = get_distance(coordinates1, coordinates2)
                if closest_distance is None or distance < closest_distance:
                    closest_so_far = identifier
                    closest_distance = distance
        return closest_so_far

    def find_close_buildings(self, identifier: int) -> set[str]:
        """Return a set of the codes of the buildings that have this intersection as their closest intersection.
        MUST be run AFTER calling self.find_closest_intersection() on all buildings.
        """
        intersection = self.intersections[identifier]
        buildings_so_far = set()

        for code, building in self.buildings.items():
            if intersection is building.closest_intersection:
                buildings_so_far.add(code)

        return buildings_so_far

    def find_shortest_path(self, id1: int,
                           id2: int) -> list[Intersection]:
        """Abstract method that returns the shortest path between the two given intersections.
        Implemented in the concrete classes, as it depends on the algorithm employed.

        Preconditions:
         - id1 in self.intersections
         - id2 in self.intersections
        """
        raise NotImplementedError


def get_distance(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    """Calculate the distance between two points on Earth, given its latitude and
    longitude coordinates.
    Assume the Earth is perfectly spherical.
    """
    lat1, long1 = p1
    lat2, long2 = p2
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    long1_rad = math.radians(long1)
    long2_rad = math.radians(long2)
    r = 6.371 * (10 ** 6)  # Earth radius
    term1 = math.sin((lat2_rad - lat1_rad) / 2) ** 2
    term2 = (math.sin((long2_rad - long1_rad) / 2) ** 2) * math.cos(lat1_rad) * math.cos(lat2_rad)
    h = term1 + term2
    d = 2 * r * math.asin(math.sqrt(h))
    return d


if __name__ == '__main__':
    import doctest

    doctest.testmod()
