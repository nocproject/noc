# ---------------------------------------------------------------------
# Attach to rack
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Iterable
from dataclasses import dataclass
from collections import defaultdict
from enum import Enum
import math

# Third-party moduls
from bson import ObjectId

# NOC modules
from noc.inv.models.object import Object
from ..result import Result


class RackSide(Enum):
    """
    Mounting side.

    Arguments:
        FRONT: Front side.
        REARL Rear side.
    """

    FRONT = "f"
    REAR = "r"

    @classmethod
    def from_str(cls, s: str) -> "RackSide":
        """
        Get from string.

        Returns:
            RackSide instance.

        Raises:
            ValueError: On invalid value.
        """
        match s:
            case "f":
                return RackSide.FRONT
            case "r":
                return RackSide.REAR
            case _:
                raise ValueError("invalid side")


@dataclass
class RackPosition(object):
    """
    Rack mounting position.
    """

    side: RackSide
    position: int

    def __hash__(self) -> int:
        return hash((self.side.value, self.position))

    @classmethod
    def from_str(cls, s: str) -> "RackPosition":
        """
        Get position from string representation.

        Format: `<side>-<position>`.

        Returns:
            RackPosition instance

        Raises:
            ValueError: on invalid format.
        """
        try:
            side, pos = s.split("-")
            return RackPosition(side=RackSide.from_str(side), position=int(pos))
        except ValueError:
            raise ValueError("invalid format")


def iter_occupied(obj: Object) -> Iterable[RackPosition]:
    """
    Iterate occupied units for object.

    Args:
        obj: Object

    Returns:
        Yield RackPosition for all occupied positions.
    """
    # Get position
    o_pos = obj.get_data("rackmount", "position")
    if not o_pos:
        return
    # Get side
    side = obj.get_data("rackmount", "side")
    if not side:
        return
    try:
        rs = RackSide.from_str(side)
    except ValueError:
        return
    # Get size in units
    units = obj.get_data("rackmount", "units")
    if not units:
        return
    # Check if object has shift
    has_shift = bool(obj.get_data("rackmount", "shift"))
    # Top position
    top = o_pos + math.ceil(units)
    if has_shift:
        top += 1
    # Mark as occupied
    for pos in range(o_pos, top):
        yield RackPosition(side=rs, position=pos)


def iter_free(
    rack: Object, /, side: RackSide | None = None, exclude: Iterable[Object] | None = None
) -> Iterable[RackPosition]:
    """
    Iterate free units from given side.

    Args:
        rack: Rack object.
        side: Restrict to given size.
        exclude: Exclude objects from free space calculations.

    Returns:
        Yields free RackPositions.
    """
    # Consume exclusions
    exclusions: set[ObjectId] | None = None
    if exclude is not None:
        exclusions = {o.id for o in exclude}
    #
    used: dict[RackSide, set[int]] = {
        RackSide.FRONT: set(),
        RackSide.REAR: set(),
    }
    # Process nested items
    for obj in rack.iter_children():
        # Exclude objects
        if exclusions and obj.id in exclusions:
            continue
        # Collect used units
        for item in iter_occupied(obj):
            used[item.side].add(item.position)
    # Yield result
    for s, u in used.items():
        if side is None or side == s:
            for pos in range(1, rack.get_data("rack", "units") + 1):
                if pos not in u:
                    yield RackPosition(side=s, position=pos)


def filter_ensured(iter: Iterable[RackPosition], /, size: int) -> Iterable[RackPosition]:
    """
    Filter rack position to have `size` free units abobe.

    Args:
        iter: RackPosition iterator.
        size: Required size.

    Returns:
        Yields valid positions.
    """
    # Consume iterator
    free: defaultdict[RackSide, set[int]] = defaultdict(set)
    for item in iter:
        free[item.side].add(item.position)
    # Yield result
    for side, avaliable in free.items():
        for unit in sorted(avaliable):
            for nu in range(unit, unit + size):
                if nu not in avaliable:
                    break
            else:
                yield RackPosition(side=side, position=unit)


def get_units(obj: Object) -> int | None:
    """
    Returns a unit size of object.

    Args:
        obj: Object instance

    Returns:
        None: if not rackmountable.
        units: Rounded up units.
    """
    u = obj.get_data("rackmount", "units")
    if u:
        return math.ceil(u)
    return None


def attach(rack: Object, obj: Object, position: RackPosition) -> Result:
    """
    Attach object to rack.

    Args:
        rack: Rack object.
        obj: Attached object.
        position: Attach position.

    Returns:
        Result status.
    """
    # Check object is rackmountable
    units = get_units(obj)
    if not units:
        return Result(status=False, message="Object is not rackmountable")
    # Get free space from given side
    free = set(filter_ensured(iter_free(rack, side=position.side, exclude=[obj]), size=units))
    if position not in free:
        return Result(status=False, message="Position is busy")
    # Attach
    obj.parent = rack
    obj.parent_connection = None
    # Set position
    obj.set_data("rackmount", "position", position.position)
    obj.set_data("rackmount", "side", position.side.value)
    obj.save()
    return Result(status=True, message="Placed to rack")


def iter_choices(rack: Object, obj: Object) -> Iterable[RackPosition]:
    """
    Iterate positions to place an object.
    """
    units = get_units(obj)
    if not units:
        return
    yield from filter_ensured(iter_free(rack, exclude=[obj]), size=units)
