# ---------------------------------------------------------------------
# ConnectionProposalBuilder
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional, Dict, Any, Iterable, Tuple, Set, List

# NOC modules
from noc.inv.models.objectmodel import ObjectModel, ObjectModelConnection
from noc.inv.models.object import Object
from noc.core.inv.path import find_path, PathItem

translation_map = str.maketrans("<>", "><")


class CrossingProposalsBuilder(object):
    def __init__(
        self,
        lo: Object,
        ro: Optional[Object] = None,
        left_filter: Optional[str] = None,
        right_filter: Optional[str] = None,
        cable_filter: Optional[str] = None,
        internal: bool = False,
    ):
        self.lo = lo
        self.ro = ro
        self.left_filter = left_filter
        self.right_filter = right_filter
        self.internal = internal
        self.cable = ObjectModel.get_by_name(cable_filter) if cable_filter else None

    def _iter_cables(self, types: set[str] | None = None) -> Iterable[Dict[str, Any]]:
        """
        Iterate over cable models.
        """
        for om in ObjectModel.objects.filter(
            data__match={"interface": "length", "attr": "length", "value__gte": 0}
        ):
            if len(om.connections) != 2:
                continue
            if types and not any(True for cc in om.connections if str(cc.type.id) in types):
                continue
            yield {"name": om.name, "available": True}

    def get_object(self, obj: Object | None) -> dict[str, Any] | None:
        """
        Get object structure.
        """
        if obj is None:
            return None
        path = [obj]
        current = obj
        while current.parent:
            current = current.parent
            path.insert(0, current)
        return {
            "path": [
                {"id": str(x.id), "label": x.parent_connection if x.parent_connection else x.name}
                for x in path
            ],
            "model": obj.model.get_short_label(),
        }

    def build(self) -> Dict[str, Any]:
        """
        Build connection proposals
        """
        result = {
            "left": {
                "connections": [],
                "internal_connections": [],
                "object": self.get_object(self.lo),
            },
            "right": {
                "connections": [],
                "internal_connections": [],
                "object": self.get_object(self.ro),
            },
            # @todo: Replace with cable lookup
            "valid": False,
            "wires": [],
        }
        left = _LeftBuilder(
            self.lo,
            self.left_filter,
            self.ro,
            self.right_filter if self.ro else None,
            self.internal,
            self.cable,
        )
        result["left"]["connections"] = list(left.iter_connections())
        result["left"]["internal_connections"] = left.internal_connections or []
        result["wires"] = left.wires
        conn_types = {c["type"] for c in result["left"]["connections"]}
        if self.ro:
            right = _RightBuilder(
                self.ro, self.right_filter, self.lo, self.left_filter, self.internal, self.cable
            )
            result["right"]["connections"] = list(right.iter_connections())
            result["right"]["internal_connections"] = right.internal_connections or []
            result["wires"].extend(right.wires)
            conn_types.update(c["type"] for c in result["right"]["connections"])
        # Add cables
        result["cable"] = list(self._iter_cables(conn_types))
        return result


class _SideBuilder(object):
    key: str
    has_wires: bool = False

    def __init__(
        self,
        o_from: Object,
        left_filter: Optional[str] = None,
        o_to: Optional[Object] = None,
        right_filter: Optional[str] = None,
        internal: bool = False,
        cable: Optional[Object] = None,
    ):
        self.o_from = o_from
        self.left_filter = left_filter
        self.o_to = o_to
        self.right_filter = right_filter
        self.internal = internal
        self.wires = []
        self.children: Optional[Dict[str, Object]] = None
        self.internal_connections = None
        self.internal_used = None
        self.cable = cable
        self.loops: set[str] = set()

    def get_children(self, name: str) -> Optional[Object]:
        """
        Get children connected to slot name.
        """
        if self.children is None:
            self.children = {
                child.parent_connection: child for child in self.o_from.iter_children()
            }
        return self.children.get(name)

    @staticmethod
    def connection_id(obj: Object, name: str) -> str:
        """
        Generate stable connection id
        """
        return f"{obj.id}{name}"

    @staticmethod
    def object_name(obj: Object) -> str:
        """
        Get full name of object.
        """
        name = " > ".join(obj.get_local_name_path(True))
        return f"{name} [{obj.model.get_short_label()}]"

    def iter_connections(self) -> Iterable[Dict[str, Any]]:
        """
        Iterate over connections and yield connections structure
        """
        # !!!>>>
        internal_used, left_cross = self.get_cross(self.o_from)
        self.internal_connections = left_cross
        self.internal_used = internal_used
        # !!!<<<
        for c in self.o_from.model.connections:
            c_data = self.o_from.get_effective_connection_data(c.name)
            r = {
                "id": self.connection_id(self.o_from, c.name),
                "name": c.name,
                "type": str(c.type.id),
                "type__label": c.type.name,
                "gender": c.gender,
                "direction": c.direction,
                "protocols": [str(p) for p in c_data.protocols],
                "internal": {"valid": True, "free": False, "allow_discriminators": []},
                "disable_reason": "",
            }
            if c.is_inner:
                r.update(self._get_inner(c))
            elif c.is_outer:
                r.update(self._get_outer(c))
            elif c.is_same_level:
                r.update(self._get_horizontal(c, c_data.protocols))
            yield r

    def is_on_map(self, obj: Object) -> bool:
        """
        Check if object is on the other side of map
        """
        return obj == self.o_to

    def _get_inner(self, c: ObjectModelConnection) -> Dict[str, Any]:
        r = {"valid": True, "free": True}
        # Apply filter
        if self.right_filter:
            r["valid"] = any(
                self.o_from.iter_connection_proposals(c.name, self.o_to.model, self.right_filter)
            )
        # Get child
        child = self.get_children(c.name)
        if not child:
            return r  # Not connected
        # Connected
        r["free"] = False
        child_outer = child.model.get_outer()
        if child_outer:
            if self.is_on_map(child):
                if self.has_wires:
                    self.wires.append(
                        [
                            {
                                "id": self.connection_id(self.o_from, c.name),
                                "name": c.name,
                                "side": "left",
                            },
                            {
                                "id": self.connection_id(child, child_outer.name),
                                "name": child_outer.name,
                                "side": "right",
                            },
                        ]
                    )
            else:
                r["remote_device"] = {
                    "name": self.object_name(child),
                    "id": str(child.id),
                    "slot": child_outer.name,
                }
        return r

    def _get_outer(self, c: ObjectModelConnection) -> Dict[str, Any]:
        r = {"valid": True, "free": True}
        # Apply filter
        if self.right_filter:
            r["valid"] = any(
                self.o_from.iter_connection_proposals(c.name, self.o_to.model, self.right_filter)
            )
        if not self.o_from.parent and not self.o_from.parent_connection:
            return r  # Not connected
        # Connected
        r["free"] = False
        if self.is_on_map(self.o_from.parent):
            if self.has_wires:
                self.wires.append(
                    [
                        {
                            "id": self.connection_id(self.o_from, c.name),
                            "name": c.name,
                            "side": "left",
                        },
                        {
                            "id": self.connection_id(
                                self.o_from.parent, self.o_from.parent_connection
                            ),
                            "name": self.o_from.parent_connection,
                            "side": "right",
                        },
                    ]
                )
        else:
            r["remote_device"] = {
                "name": self.object_name(self.o_from.parent),
                "id": str(self.o_from.parent.id),
                "slot": self.o_from.parent_connection,
            }
        return r

    def _get_horizontal(self, c: ObjectModelConnection, protocols) -> Dict[str, Any]:
        r = {"valid": True, "free": True}
        oc, _, _ = self.o_from.get_p2p_connection(c.name)
        # Deny same and internal <-> external
        if self.left_filter == c.name and self.key == "left":  # @todo
            # Same connection
            valid = False
        elif self.o_to or self.cable:
            valid = any(
                self.o_from.iter_connection_proposals(
                    c.name,
                    self.cable or self.o_to.model,
                    self.right_filter if not self.cable else None,
                )
            )
        else:
            valid = not self.internal and c.type.name != "Composed"
        #
        r["free"] = not oc
        r["valid"] = valid
        if self.o_from.model.has_connection_cross(c.name):
            # Allowed crossed input
            r["internal"] = {
                "valid": c.name != self.left_filter and not (self.internal and self.left_filter),
                "free": c.name not in self.internal_used,
                "allow_discriminators": [],
            }
            if self.internal and self.left_filter:
                rc = self.o_from.get_crossing_proposals(c.name, self.left_filter)
                if rc:
                    r["internal"].update(
                        {"valid": True, "free": True, "allow_discriminators": rc[0][1]}
                    )
        if oc:
            rd = self.get_remote_device(c.name, protocols, self.o_from)
            if rd and not self.is_on_map(rd.obj):
                r["remote_device"] = {
                    "name": self.object_name(rd.obj),
                    "id": str(rd.obj.id),
                    "slot": rd.connection,
                }
            is_loop = False
            if not rd:
                loop_side = self.get_loopback_connection(self.o_from, c.name)
                if loop_side:
                    is_loop = True
                    if loop_side not in self.loops:
                        self.loops.add(c.name)
                        self.loops.add(loop_side)
                        side = "left" if self.has_wires else "right"
                        self.wires.append(
                            [
                                {
                                    "id": self.connection_id(self.o_from, c.name),
                                    "name": c.name,
                                    "side": side,
                                },
                                {
                                    "id": self.connection_id(self.o_from, loop_side),
                                    "name": loop_side,
                                    "side": side,
                                },
                            ]
                        )
            if self.has_wires and self.o_to and not is_loop:
                _, remote = self.get_remote_slot(c, self.o_from, self.o_to)
                if remote:
                    self.wires.append(
                        [
                            {
                                "id": self.connection_id(self.o_from, c.name),
                                "name": c.name,
                                "side": "left",
                            },
                            {
                                "id": self.connection_id(self.o_to, remote.connection),
                                "name": remote.connection,
                                "side": "right",
                            },
                        ]
                    )
        return r

    @staticmethod
    def get_remote_device(slot, protocols, o) -> PathItem | None:
        """
        Determing remote device with find_path method
        :return:
        """
        for path in (
            find_path(
                o, slot, [str(p).translate(translation_map) for p in protocols], trace_wire=True
            )
            or []
        ):
            if path.obj != o and not path.obj.is_wire:
                return path
        return None

    @staticmethod
    def get_remote_slot(left_slot, lo, ro):
        """
        Determine right device's slot with find_path method
        :return:
        """
        wire = None
        for path in (
            find_path(
                lo,
                left_slot.name,
                [str(p).translate(translation_map) for p in left_slot.protocols],
                trace_wire=True,
            )
            or []
        ):
            if path.obj.is_wire:
                wire = path.obj
            if path.obj == ro:
                return wire, path
        return None, None

    def get_cross(self, o: Object) -> Tuple[Set[str], List[Dict[str, Any]]]:
        r, used = [], set()
        for s, ss in [("model", o.model), ("object", o)]:
            for c in ss.cross:
                r += [
                    {
                        "from": {
                            "id": f"{str(o.id)}{c.input}",
                            "name": c.input,
                            "has_arrow": False,
                            "discriminator": self.format_discriminator(c.input_discriminator or ""),
                        },
                        "to": {
                            "id": f"{str(o.id)}{c.output}",
                            "name": c.output,
                            "has_arrow": True,
                            "discriminator": self.format_discriminator(
                                c.output_discriminator or ""
                            ),
                        },
                        "gain_db": c.gain_db or 1.0,
                        "is_delete": s == "object",
                    }
                ]
                used |= {c.input, c.output}
        return used, r

    @staticmethod
    def format_discriminator(d) -> str:
        if not d:
            return d
        prefix, d = d.split("::", 1)
        if prefix == "lambda":
            return f"{chr(955)}{d}"
        return d

    def get_loopback_connection(self, obj: Object, name: str) -> str | None:
        """
        Find other side of loopback connection
        """
        _, ro, rn = obj.get_p2p_connection(name)
        if not ro or not ro.is_wire:
            return None
        # Find other part
        for oc in ro.iter_cross(rn):
            _, rro, rrn = ro.get_p2p_connection(oc.output)
            if rro and rro == obj:
                return rrn
        return None


class _LeftBuilder(_SideBuilder):
    key = "left"
    has_wires = True


class _RightBuilder(_SideBuilder):
    key = "right"
