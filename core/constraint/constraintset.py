# ----------------------------------------------------------------------
# ConstraintSet class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict
from typing import Iterable, TypeVar

# NOC modules
from .base import BaseConstraint

BC = TypeVar("BC", bound=BaseConstraint)


class ConstraintSet(object):
    """
    Set of restrictions.
    """

    def __init__(self: "ConstraintSet") -> None:
        self._data: defaultdict[type[BaseConstraint], list[BaseConstraint]] = defaultdict(list)

    def get(self: "ConstraintSet", item: type[BC]) -> list[BC] | None:
        """
        Get item.

        Args:
            item: Type of constraint.

        Returns:
            List of constraints: If found.
            None: otherwise.
        """
        return self._data.get(item)

    @classmethod
    def from_iter(cls: "type[ConstraintSet]", iter: Iterable[BaseConstraint]) -> "ConstraintSet":
        r = cls()
        for item in iter:
            r.extend(item)
        return r

    def __iter__(self: "ConstraintSet") -> Iterable[BaseConstraint]:
        for items in self._data.values():
            yield from items

    def extend(self: "ConstraintSet", item: BaseConstraint) -> None:
        """
        Add new possibility.

        Loosen current restrictions if any, or add it if empty.

        Args:
            item: Additional restriction item.
        """
        self._data[type(item)].append(item)

    def intersect(self: "ConstraintSet", other: "ConstraintSet") -> "ConstraintSet | None":
        """
        Intersect restrictions.

        Args:
            other: Restrictions to intersect.

        Returns:
            Resulting restrictions set, if possibile. `None` otherwise.
        """

        def iter_intersect(
            left: list[BaseConstraint], right: list[BaseConstraint]
        ) -> Iterable[BaseConstraint]:
            for l_item in left:
                for r_item in right:
                    if l_item.satisfy(r_item):
                        yield l_item
                        break

        if self.is_empty():
            return other
        if other.is_empty():
            return self
        r = ConstraintSet()
        for key, left in self._data.items():
            right = other._data[key]
            if right:
                items = list(key.iter_optimize(iter_intersect(left, right)))
                if items:
                    r._data[key] = items
            else:
                r._data[key] = left
        # Copy new from other
        for key in set(other._data) - set(self._data):
            r._data[key] = other._data[key]
        if r._data:
            return r
        return None

    def is_empty(self: "ConstraintSet") -> bool:
        return not self._data
