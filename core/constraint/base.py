# ----------------------------------------------------------------------
# BaseConstraint class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Iterable


class BaseConstraint(object):
    """
    Base constraint class.

    Represents a single restriction.

    Subclasses must implement `__eq__` and `__str__ methods.
    """

    def __repr__(self: "Constraint") -> str:
        tn = self.__class__.__name__
        return f"<{tn} {str(self)}>"

    def __eq__(self: "Constraint", value: object) -> bool: ...
    def satisfy(self: "Constraint", item: "Constraint") -> bool:
        """
        Check if constraint satisfies condition.

        Args:
            item: Constraint condition.

        Returns:
            True: if constraint satisfies condition.
            False: Otherwise.
        """
        if type(self) != type(item):
            msg = f"Cannot satisfy {type(self)} over {type(item)}"
            raise ValueError(msg)
        return self == item

    @classmethod
    def iter_optimize(
        cls: "type[Constraint]", iter: "Iterable[Constraint]"
    ) -> "Iterable[Constraint]":
        """
        Optimize sequence of constraint.

        Merge adjanced when necessary.

        Args:
            iter: Iterable of constraints.

        Returns:
            Iterable of optimized constraints.
        """
        yield from iter
