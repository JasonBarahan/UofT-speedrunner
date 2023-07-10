"""
UofT Speedrunner

Module Description
==================
This file contains entities used to represent various features of the map in
terms of graphs. Buildings and intersections are represented as nodes, while
paths between these buildings and intersections are represented as edges.
These are represented using an AbstractGrid object which can be further used
to find nearby buildings from a given intersection, and shortest paths
between two buildings.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of the students
mentioned below and all CSC111 course staff at the University of Toronto.
Any other parties not mentioned may not use or possess copies of
this code, whether modified or otherwise.

This file is Copyright (c) 2023 
Jason Barahan, Vibhas Raizada, Benjamin Sandoval, Eleonora Scognamiglio.
"""
from __future__ import annotations
from typing import Optional, Any
from python_ta.contracts import check_contracts
import math

# Global variables
AMENITIES = {
    'study', 'dining', 'coffee', 'microwave', 'gym', 'library', 'atm',
    'math learning centre', 'writing centre', 'transportation'
}


@check_contracts
class Building:
    """
      A class for the buildings within the UofT campus.

      Instance Attributes:
      - code: a string containing a two-letter unique building
        identifier
      - closest_intersection: the Intersection closest to the building's
        main entrance
      - amenities: a list of strings specifying amenities available.
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


@check_contracts
class Intersection:
    """
      A class for the intersections (nodes) within the UofT campus.

      Instance Attributes:
      - identifier: intersection id
      - name: a set of strings intersecting at this point
      - close_buildings: a set of buildings closest to this intersections
      - coordinates: a tuple consisting of (longitude, latitude)
      - edges: edges connected to this intersection

      Representation Invariants:
       - self.close_buildings == set() or all(self.coordinates == b.closest_intersection.coordinates for b in self.close_buildings)
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

            close_buildings is EMPTY as we are determining the close buildings
            after the fact.
            edges is EMPTY as adjacent intersections will be determined after-the-fact.
            """
        self.identifier = identifier
        self.name = name
        self.close_buildings = set()  # empty
        self.coordinates = coordinates
        self.edges = set()  # edges are empty


@check_contracts
class Edge:
    """
      The 'roadway' connecting two Intersections.
      Edges are weighted by travel time between Intersections.

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
        lat_1, long_1 = intersection1.coordinates
        lat_2, long_2 = intersection2.coordinates
        distance = math.dist([lat_1, long_1], [lat_2, long_2])
        self.distance = distance

    def get_other_endpoint(self, intersection: Intersection) -> Intersection:
        """Return the endpoint of this Edge that is not equal to the given intersection.

        Preconditions:
            - intersection in self.endpoints
        """
        return (self.endpoints - {intersection}).pop()


@check_contracts
class AbstractGrid:
    """
    The map of U of T.

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
        """Finds the intersection with the closest Euclidean distance to that of the building.
        Used for the initialization of all buildings.
            Input: The building code.
            Output: The ID of the intersection.
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
                # lat_1, long_1 = intersection.coordinates
                # lat_2, long_2 = self.buildings[building_code].coordinates
                # distance = math.dist([lat_1, long_1], [lat_2, long_2])
                coordinates1 = intersection.coordinates
                coordinates2 = self.buildings[building_code].coordinates
                distance = get_distance(coordinates1, coordinates2)
                if closest_distance is None or distance < closest_distance:
                    closest_so_far = identifier
                    closest_distance = distance
        return closest_so_far

    def find_close_buildings(self, identifier: int) -> set[str]:
        """Return a set of the codes of the buildings closest to a given intersection.
        MUST be run AFTER calling self.find_closest_intersection() on all buildings.
        """
        intersection = self.intersections[identifier]
        buildings_so_far = set()

        for code, building in self.buildings.items():
            if intersection is building.closest_intersection:
                buildings_so_far.add(code)

        return buildings_so_far

    def find_shortest_path(self, id1: int, id2: int) -> list[Edge]:
        """Retturn the shortest path between the two given intersections

        Preconditions:
         - ... TODO
        """
        raise NotImplementedError


# TODO: introduce an unimplemented method so it is abstract


def get_distance(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    """Calculate the distance between two points on Earth, given its latitude and
    longitude coordinates.
    Assume the Earth is perfectly spherical
    """
    lat1, long1 = p1
    lat2, long2 = p2
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    long1_rad = math.radians(long1)
    long2_rad = math.radians(long2)
    r = 6.371 * (10**6)  # Earth radius
    term1 = math.sin((lat2_rad - lat1_rad) / 2)**2
    term2 = (math.sin((long2_rad - long1_rad) / 2)**
             2) * math.cos(lat1_rad) * math.cos(lat2_rad)
    h = term1 + term2
    d = 2 * r * math.asin(math.sqrt(h))
    return d


# # BUILDING SELECTION TOOLS
# def select_building_with_amenity(location: ent.Building | ent.Intersection, amenity: str) -> ent.Building:
#     """
#     Selects the closest building with a specified amenity.
#     """
#
#
# # PATH GENERATION TOOLS
# def get_shortest_path(start: ent.Building,
#                       end: ent.Building) -> dict[ent.Building | ent.Intersection]:
#     """
#     Generate the shortest path between two nodes.
#     In this case, paths are collections of nodes.
#     """
#
#
# def get_path_includes_node(start: ent.Building, end: ent.Building, includes: ent.Building) -> dict[
#     ent.Building | ent.Intersection]:
#     """
#     Generate the shortest path between two nodes that INCLUDES a certain node.
#     This can be an endpoint or an intermediary node.
#     """
#
#
# def AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA(aaa: int, aaaa: int) -> int:
#     """
#     Procrastinate
#     """
