"""
UofT Speedrunner

Module Description
==================
This file contains classes for the concrete grids being used for our various path-finding algorithms used throughout our
program, as well as entities for PriorityQueue, which is required for our implementation of one of our algorithms. There
is a class for a grid created using depth-first search, and a class for another grid created using an implementation of
Djikstra's algorithm.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of the students
mentioned below and all CSC111 course staff at the University of Toronto.
Any other parties not mentioned may not use or possess copies of
this code, whether modified or otherwise.

This file is Copyright (c) 2023.
Jason Barahan, Vibhas Raizada, Benjamin Sandoval, Eleonora Scognamiglio.
"""
import math
from entities import Building, Intersection, AbstractGrid, Edge


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

        * Not implemented yet TODO: Can someobody check what this line beside me means? idk
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
                path_distance = sum(e.distance for e in path)
                if path_distance < shortest_so_far:
                    shortest_so_far = path_distance
                    shortest_path_so_far = path
        else:
            for path in all_paths:
                # 3. B. In this case, make a list (or set, doesn't matter) of all intersection IDs we've been to.
                # This way, we can simply check that all the intermediates are in the path.
                list_of_ids = []
                for edge in path:
                    list_of_ids.extend(
                        [endpoint.identifier for endpoint in edge.endpoints])
                if all(intermediate in list_of_ids
                       for intermediate in intermediates):
                    # 3. C. If this is the case: continue checking by comparing path distances.
                    path_distance = sum(e.distance for e in path)
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

    def find_shortest_path(self, id1: int, id2: int) -> list[Edge]:
        """Find the shortest path between two intertersections in the Dijkstra Grid.
        We treat #1 as the START and #2 as the END.
        Input: The identifiers of the two intersections.
        Output: All intersections, in order, to visit (including intersection1 and intersection 2).
        """
        path_of_intersections = self.find_path_dijkstra(id1, id2)

        # convert the list of intersection into a list of edges
        if not path_of_intersections:
            print('Sorry, it seems like your destination is not reacheable :(')
        else:
            path_with_edges = []
            for i in range(len(path_of_intersections) - 1):
                first_intersection = self.intersections[
                    path_of_intersections[i]]
                second_intersection = self.intersections[path_of_intersections[
                    i + 1]]
                edge = first_intersection.find_edge(second_intersection)
                path_with_edges.append(edge)
            return path_with_edges

    def find_path_dijkstra(self, id1: int, id2: int) -> list[int]:
        """Method that calculates the most optimal path from id1 to id2 using an implementation of Dijkstra's
        algorithm. This implementation uses a Priority Queue, and some minor adjustments have been made in the base
        logic of the algorithm to practically accomodate for our code and purposes (further details in the report)
        """
        source = self.intersections[id1]  # source is the intersection object corresponding to integer id1

        labeled_intersections = {
            i.identifier: [math.inf, id1]
            for i in self.intersections.values()
        }  # labelled_intersections is a dictionary of intersections that stores the id of an intersection as key and
        # a list containing the known distance from start to this intersection and last intersection visited as value
        labeled_intersections[source.identifier] = [0, None]
        dequeued = []
        queue = _PriorityQueue()

        # enqeueue all intersections with an initial distance and previous node
        for intersection_id in self.intersections:
            if intersection_id == id1:
                distance = 0
                prev_id = None
            else:
                distance = math.inf
                prev_id = id1
            queue.enqueue(distance, intersection_id, prev_id)

        while not queue.is_empty() and id2 not in [i[0] for i in dequeued]:
            current_id = queue.dequeue()
            current_intersection = self.intersections[current_id]
            for edge in current_intersection.edges:  # for every edge connected to this intersection
                neighbour = edge.get_other_endpoint(current_intersection)  # getting a neighbour to that intersection
                new_distance = labeled_intersections[current_id][0] + edge.distance
                old_distance = labeled_intersections[neighbour.identifier][0]
                if new_distance < old_distance:
                    queue.remove(neighbour.identifier)
                    queue.enqueue(new_distance, neighbour.identifier,
                                  current_id)
                    labeled_intersections[neighbour.identifier] = [new_distance, current_id]

            prev = labeled_intersections[current_id][1]
            dequeued.append((current_id, prev))

        if id2 in [i[0] for i in dequeued]:
            path_of_ids = self.traceback_dijkstra(dequeued)
            return path_of_ids
        else:  # queue.is_empty and destination was not dequeued => we haven't found a path
            return []

    def traceback_dijkstra(self,
                           dequeued: list[tuple[int, int]]) -> list[int]:
        """Helper method for finding an optimal path between intersections using Dijkstra's algorithm. Traces back
        through the deqeued intersections to find the true optimal path calculated using the algorithm."""
        path_so_far = []  # creating list of our path, starting with adding in the final node
        last_item = dequeued[-1]

        popped = dequeued.pop()

        assert last_item == popped

        path_so_far.append(last_item[0])
        next_item = last_item[1]

        while dequeued:
            popped = dequeued.pop()
            if next_item == popped[0]:
                path_so_far.append(popped[0])
                next_item = popped[1]

        path_so_far.reverse()

        return path_so_far


class EmptyPriorityQueueError(Exception):
    """Exception raised when calling pop on an empty priority queue."""

    def __str__(self) -> str:
        """Return a string representation of this error."""
        return 'You called dequeue on an empty priority queue.'


class _PriorityQueue:
    """A queue of items that can be dequeued in priority order.

    When removing an item from the queue, the highest-priority item is the one
    that is removed.
    """
    # Private Instance Attributes:
    #   - _items: a list of the items in this priority queue
    _items: list[tuple[float, int, int]]

    def __init__(self) -> None:
        """Initialize a new and empty priority queue."""
        self._items = []

    def is_empty(self) -> bool:
        """Return whether this priority queue contains no items.
        """
        return self._items == []

    def enqueue(self, distance: float, item_id: int, prev_id: int) -> None:
        """Add the given item with the given priority to this priority queue.
        # >>> q = _PriorityQueue()
        # >>> q.enqueue(9, 'A')
        # >>> q.enqueue(5, 'B')
        # >>> q.enqueue(3, 'C')
        # >>> q.enqueue(1, 'D')
        # >>> q._items
        # [(9, 'A'), (5, 'B'), (3, 'C'), (1, 'D')]
        # >>> q.enqueue(4, 'E')
        # >>> q._items
        # [(9, 'A'), (5, 'B'), (4, 'E'), (3, 'C'), (1, 'D')]
        # >>> q.dequeue()
        # 'D'
        # >>> q._items
        # [(9, 'A'), (5, 'B'), (4, 'E'), (3, 'C')]
        """

        # (0, 1, None)
        # (inf, 2, 1)

        # (inf, 1, 47)
        # (inf, 2, 47)

        i = len(self._items) - 1   # getting index of last item
        while i >= 0 and self._items[i][0] < distance:  # ADDED THE EQUALS
            # Loop invariant: all items in self._items[0:i]
            # have a lower priority than <priority>.
            i -= 1

        self._items.insert(i + 1, (distance, item_id, prev_id))

    def dequeue(self) -> int:
        """Remove and return the item with the highest priority.

        Raise an EmptyPriorityQueueError when the priority queue is empty.
        """
        if self.is_empty():
            raise EmptyPriorityQueueError
        else:
            _priority, item_id, _prev_id = self._items.pop()
            return item_id

    def __contains__(self, item_id: int) -> bool:
        """Check if contained in Priority Queue.
        """
        items = [i[1] for i in self._items]
        return item_id in items

    def remove(self, item_id: int) -> int:
        """Remove and return a specific item."""
        ids = [j[1] for j in self._items]
        i = ids.index(item_id)
        return self._items.pop(i)[1]


if __name__ == '__main__':
    import doctest

    doctest.testmod()

    # import python_ta
    #
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['E9992', 'E9997', 'E9999', 'E9969', 'R1702', 'E9998', 'R1710', 'R0914']
    # })
