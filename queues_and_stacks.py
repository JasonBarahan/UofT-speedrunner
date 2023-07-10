# TODO: general code review

"""
UofT Speedrunner

Module Description
==================
This file contains implementations of the queue and stack ADTs.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of the students
mentioned below and all CSC111 course staff at the University of Toronto.
Any other parties not mentioned may not use or possess copies of
this code, whether modified or otherwise.

This file is Copyright (c) 2023 
Jason Barahan, Vibhas Raizada, Benjamin Sandoval, Eleonora Scognamiglio.
"""
from typing import Any


# exception handling
class EmptyStackError(Exception):
    """Exception raised when calling pop on an empty priority queue."""

    def __str__(self) -> str:
        """Return a string representation of this error."""
        return 'This stack is empty and has nothing to return.'


class EmptyPriorityQueueError(Exception):
    """Exception raised when calling pop on an empty priority queue."""

    def __str__(self) -> str:
        """Return a string representation of this error."""
        return 'You called dequeue on an empty priority queue.'


# ADT implementations
class PriorityQueue:
    """A queue of items that can be dequeued in priority order.

    When removing an item from the queue, the highest-priority 
    item is the one that is removed.
    """
    # Private Instance Attributes:
    #   - _items: a list of the items in this priority queue
    _items: list[tuple[int, Any]]

    def __init__(self) -> None:
        """Initialize a new and empty priority queue."""
        self._items = []

    def is_empty(self) -> bool:
        """Return whether this priority queue contains no items.
        """
        return self._items == []

    def enqueue(self, distance: int, item: Any) -> None:
        """Add the given item with the given priority to this priority queue.
        >>> q = PriorityQueue()
        >>> q.enqueue(9, 'A')
        >>> q.enqueue(5, 'B')
        >>> q.enqueue(3, 'C')
        >>> q.enqueue(1, 'D')
        >>> q._items
        [(9, 'A'), (5, 'B'), (3, 'C'), (1, 'D')]
        >>> q.enqueue(4, 'E')
        >>> q._items
        [(9, 'A'), (5, 'B'), (4, 'E'), (3, 'C'), (1, 'D')]
        >>> q.dequeue()
        'D'
        >>> q._items
        [(9, 'A'), (5, 'B'), (4, 'E'), (3, 'C')]
        """
        i = len(self._items) - 1
        while i > 0 and self._items[i][0] < distance:
            # Loop invariant: all items in self._items[0:i]
            # have a lower priority than <priority>.
            i -= 1

        self._items.insert(i + 1, (distance, item))

    def dequeue(self) -> Any:
        """Remove and return the item with the highest priority.

        Raise an EmptyPriorityQueueError when the priority queue is empty.
        """
        if self.is_empty():
            raise EmptyPriorityQueueError
        else:
            _priority, item = self._items.pop()
            return item
