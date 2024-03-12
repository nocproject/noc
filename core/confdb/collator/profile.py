# ----------------------------------------------------------------------
# Profile methods collator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Optional, List

# NOC modules
from .base import BaseCollator


@dataclass(frozen=True)
class PathItem(object):
    # Components: path, c_name, c_num, stack_num, slot_num, protocol_prefix
    context: str
    c_name: str  # Connection name
    c_num: int  # Connection num
    path_template: Optional[str] = None
    stack_num: Optional[int] = None
    slot_num: Optional[str] = None

    @classmethod
    def from_object(cls, o: "Object", c: "ObjectModelConnection") -> "PathItem":
        p = PathItem(
            context=o.model.cr_context,
            c_name=c.name,
            c_num=c.name,
            path_template=o.get_data("interface_collation", "path_template"),
            stack_num=o.get_data("stack", "member"),
            # slot_num=o.get_data("slot", "number"),
        )
        return p

    def __str__(self):
        return f"{self.c_name} ({self.context})"


@dataclass
class PortItem(object):
    name: str
    protocols: List[str]
    path: List[PathItem]
    internal_name: str

    @property
    def context(self) -> str:
        return self.path[-1].context

    @property
    def stack_num(self) -> int:
        return self.path[0].stack_num

    @property
    def slot_num(self) -> str:
        return self.path[0].slot_num

    @property
    def protocol_prefix(self) -> str:
        p = sorted(self.protocols)
        return p[-1].get_data("interface_collation", "protocol_prefixes")


class ProfileCollator(BaseCollator):
    """
    Direct map between connection name and interface name
    """

    def collate(self, physical_path, interfaces):

        c = physical_path[-1].connection
        pi = PortItem(
            name=c.name,
            protocols=[p.protocol.code for p in c.protocols],
            path=[PathItem.from_object(p.object, p.connection) for p in physical_path[:-1]],
            internal_name=c.internal_name,
        )
        for iface_name in self.profile.get_interfaces_by_port(pi):
            iface_name = self.profile.convert_interface_name(iface_name)
            if iface_name in interfaces:
                return interfaces[iface_name]
