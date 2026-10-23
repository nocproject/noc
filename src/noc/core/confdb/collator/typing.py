# ----------------------------------------------------------------------
# BaseCollator types
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PathItem:
    """Connection Path. From chassis to last module"""

    # Components: path, c_name, c_num, stack_num, slot_num, protocol_prefix
    object: Any
    connection: Any
    context: str  # Model Context
    c_name: str  # Connection name
    path_template: str | None = None
    stack_num: int | None = None  # Number of stack (if stackable)
    slot_num: str | None = None  # number from get_inventory output

    @classmethod
    def from_object(cls, o, c) -> "PathItem":
        stackable = o.get_data("stack", "stackable")
        return PathItem(
            object=o,
            connection=c,
            context=o.model.cr_context,
            c_name=c.name,
            # path_template=o.get_data("interface_collation", "path_template"),
            stack_num=o.get_data("stack", "member") or 0 if stackable else None,
            # slot_num=o.get_data("slot", "number"),
        )

    def __str__(self) -> str:
        return f"{self.c_name} ({self.context})"


@dataclass
class PortItem:
    """Connection port, by selected protocols"""

    name: str
    protocols: list[str]
    path: list[PathItem]
    internal_name: str | None = None
    combo: str | None = None

    @property
    def context(self) -> str:
        return self.path[-1].context

    @property
    def stack_num(self) -> int | None:
        return self.path[0].stack_num

    @property
    def slot_num(self) -> str:
        return self.path[-1].slot_num
