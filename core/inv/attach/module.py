# ---------------------------------------------------------------------
# Attach to module
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Iterable

# NOC modules
from noc.inv.models.objectmodel import ObjectModel
from noc.inv.models.object import Object
from noc.inv.models.error import ConnectionError
from noc.core.resource import from_resource
from ..result import Result


@dataclass
class ModulePosition(object):
    obj: Object
    name: str
    parent: Object | str

    def as_resource(self) -> str:
        """
        Convert position to resource.
        """
        return f"o:{self.obj.id}:{self.name}"

    @classmethod
    def from_resource(cls, res: str) -> "ModulePosition":
        """
        Get position from resource.
        """
        obj, name = from_resource(res)
        return ModulePosition(obj=obj, name=name)


def attach(obj: Object, /, position=ModulePosition) -> Result:
    """
    Insert module into object.

    Args:
        obj: attached item.
        position: position to attach.

    Returns:
        Result item.
    """
    try:
        obj.attach(position.obj, position.name)
    except ConnectionError as e:
        return Result(status=False, message=str(e))
    return Result(status=True, message="Item attached")
