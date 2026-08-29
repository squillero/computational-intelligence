# Copyright © 2026 Giovanni Squillero / Politecnico di Torino
# https://github.com/squillero/programmer-zendo
# Free under certain conditions — see the license for details.

"""Minimalistic Updatable Priority Queue using a lazy-deletion heap.

Notes:
- The order of different items with the same priority is not specified.
"""

import heapq
from collections.abc import Iterator


class UPQ:
    _data: list[tuple[object, object]]
    _priority: dict

    def __init__(self, data=tuple()) -> None:
        """Create a new UPQ, possibly initialized with data."""
        self._data = list()
        self._priority = dict()
        for i in data:
            self.push_update(*i)

    def __getitem__(self, item) -> object:
        """Return the priority of an item."""
        return self._priority[item]

    def __len__(self) -> int:
        """Return the number of items in the queue."""
        return len(self._priority)

    def __bool__(self) -> bool:
        """Return True if the queue is not empty."""
        return bool(self._priority)

    def __delitem__(self, item) -> None:
        """Delete an item from the queue."""
        del self._priority[item]

    def __contains__(self, item) -> bool:
        """Check if item is in the queue."""
        return item in self._priority

    def __iter__(self) -> Iterator[tuple[object, object]]:
        """Iterate in priority order without modifying the queue."""
        return iter(sorted(self._priority.items(), key=lambda k: k[1]))

    def get(self, item, default=None) -> object:
        """Return the priority of an item, or default if not present."""
        return self._priority.get(item, default)

    def push_update(self, item, priority) -> None:
        """Push a new item with the given priority or update its priority."""
        self._priority[item] = priority
        heapq.heappush(self._data, (priority, item))

    def pop(self) -> tuple[object, object]:
        """Pop the item with the lowest priority. Fails if empty."""
        p, i = heapq.heappop(self._data)
        while p != self._priority.get(i):
            p, i = heapq.heappop(self._data)
        del self._priority[i]
        return (i, p)

    def pop_safe(self, default=None) -> tuple[object, object] | object:
        """Pop the item with the lowest priority. Return `default` if the queue is empty."""
        while self._data:
            p, i = heapq.heappop(self._data)
            if p == self._priority.get(i):
                del self._priority[i]
                return (i, p)
        else:
            return default
