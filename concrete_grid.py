# map generation helper functions
from test_new_entities import Building, Intersection, AbstractGrid, Edge
import math


# def generate_map() -> None:
class DFSGrid(AbstractGrid):
    """A concrete class for AbstractGrid.
    It finds the shortest path between two buildings using a Depth First Search Algorithm
    """

    def __init__(self, intersections: dict[int, Intersection],
                 buildings: dict[str, Building]) -> None:
        """Initialize a DFSGrid object, representing a map of the U of T campus"""
        AbstractGrid.__init__(self, intersections, buildings)

    def find_shortest_path(self, id1: int, id2: int, intermediates: set[int] = None, max_distance: int = 2000) \
            -> list[Edge]:
        """Find the shortest path between two intertersections in the grid (using DFS) while accounting for
        any intermediate and unordered intersections along the way.

        If no path exists that traverses through *all* intermediate intersections in an allotted total distance length,
        a path list will be returned that goes through as many as possible. *

        id1: The starting intersection.
        id2: The ending intersection.
        intermediates: The set of intesection identifiers that can be visited in any order in between
         visiting id1 and id2. If nothing is passed, it is defaulted to None.
        max_distance: The maximum distance (in meters) of the total path distance that the algorithm will check.
         Set to 2000m (2km) by default. 2000m will take about 4 seconds with an empty intermediates set.
         3000m will take about 15 seconds with the same set.

         NOTE: if the algorith is returning None, this may be because you inputted many intermediates and
          a path cannot be found under the given max_distance. To fix this, try increasing the max_distance parameter
          by increments of 500m until a path is returned.

        * Not implemented yet
        """
        # 1. Store all the paths (under a certain total distance) in a single list.
        start_intersection = self.intersections[id1]
        all_paths = start_intersection.find_all_paths(id2, set(), max_distance)

        # 2. Fix the variables to store the shortest path.
        shortest_so_far = math.inf
        shortest_path_so_far = []

        # 3. Loop through all the paths.
        if intermediates is None or len(intermediates) == 0:
            # 3. A. In this case, we have no intermedidate intersections.
            for path in all_paths:
                path_distance = sum(edge.distance for edge in path)
                if path_distance < shortest_so_far:
                    shortest_so_far = path_distance
                    shortest_path_so_far = path
        else:
            for path in all_paths:
                # 3. B. In this case, make a list (or set, doesn't matter) of all intersection IDs we've been to.
                # This way, we can simply check that all the intermediates are in the path.
                list_of_ids = []
                for edge in path:
                    list_of_ids.extend([endpoint.identifier for endpoint in edge.endpoints])
                # print(list_of_ids])
                if all(intermediate in list_of_ids for intermediate in intermediates):
                    # 3. C. If this is the case: continue checking by comparing path distances.
                    path_distance = sum(edge.distance for edge in path)
                    if path_distance < shortest_so_far:
                        shortest_so_far = path_distance
                        shortest_path_so_far = path

        return shortest_path_so_far


class DijkstraGrid(AbstractGrid):
    """Grid algorithms implemented using the Dijkstra algorithm."""

    def __init__(self, intersections: dict[int, Intersection],
                 buildings: dict[str, Building]) -> None:
        """Initialize a DijkstraGrid object, representing a map of the U of T campus"""
        AbstractGrid.__init__(self, intersections, buildings)

    def find_shortest_path(self, id1: int,
                           id2: int) -> list[Edge]:
        """Find the shortest path between two intertersections in the Dijkstra Grid.
        We treat #1 as the START and #2 as the END.
        Input: The identifiers of the two intersections.
        Output: All intersections, in order, to visit (including intersection1 and intersection 2).
        """
        # TODO
