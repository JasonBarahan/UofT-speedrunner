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
            print('Sorry, it seems like your destination is not reachable :(')
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
            path_of_ids = self.traceback_dijkstra(id2, dequeued)
            return path_of_ids
        else:  # queue.is_empty and destination was not dequeued => we haven't found a path
            return []

    def traceback_dijkstra(self, goal: int,
                           dequeued: list[tuple[int, int]]) -> list[int]:
        """Helper method for finding an optimal path between intersections using Dijkstra's algorithm. Traces back
        through the deqeued intersections to find the true optimal path calculated using the algorithm."""
        path_so_far = [goal]  # creating list of our path, starting with adding in the final node
        useful_dict = {i[0]: i[1] for i in dequeued}

        last_item = dequeued[-1]

        popped = dequeued.pop()
        while dequeued:
            while popped != last_item:
                popped = dequeued.pop()
            path_so_far.append(popped[1])
            if popped[1] is not None:
                last_item = (useful_dict[popped[0]], useful_dict[popped[1]])  # this part gives error with TT
                popped = dequeued.pop()

        assert last_item == popped
        path_so_far.append(popped[0])

        path_so_far.reverse()

        # See the written report under "Dijkstra" for an explanation of this if statement
        if None in path_so_far:
            path_so_far = path_so_far[2:]
        else:
            path_so_far = path_so_far[1:]

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
        while i >= 0 and self._items[i][0] < distance: # ADDED THE EQUALS
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