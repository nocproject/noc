# ----------------------------------------------------------------------
# Inventory path finder
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Iterable, List, Set, Dict, DefaultDict
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict
from itertools import permutations

# NOC modules
from noc.inv.models.object import Object
from noc.inv.models.objectconnection import ObjectConnection
from noc.inv.models.protocol import ProtocolVariant


class ConnAction(int, Enum):
    REJECT = 0
    PASS = 1
    FOUND = 2


@dataclass(frozen=True)
class PathItem(object):
    obj: Object
    connection: str


@dataclass(frozen=True)
class AdjItem(object):
    local_name: str
    remote_object: Object
    remote_name: str


def find_path(
    obj: Object, connection: str, target_protocols: Iterable[str], max_depth=100, trace_wire=False
) -> Optional[List[PathItem]]:
    """
    Build shortest path from object's connection until a connection with any of the
    target protocols found.

    :param obj: Object instance
    :param connection: Starting connection name
    :param target_protocols: Iterable of protocols
    :param max_depth: Path Limit
    :param trace_wire: Tracing Wire connection (return neighbor conncted by wire)
    :return:
    """

    def get_action(ro: Object, r_name: str) -> ConnAction:
        """
        Check peer connection and return action
        :param ro: Object reference
        :param r_name: connection name
        :return:
        """
        mc = ro.model.get_model_connection(r_name)
        if not mc:
            return ConnAction.REJECT
        if trace_wire and not ro.is_wire:
            return ConnAction.FOUND
        if not mc.protocols:
            return ConnAction.PASS
        if any(p for p in mc.protocols if p in tp):
            return ConnAction.FOUND
        return ConnAction.REJECT

    def iter_path(final: PathItem) -> Iterable[PathItem]:
        def iter_reconstruct(pp: PathItem) -> Iterable[PathItem]:
            b = prev.get(pp)
            if b:
                yield from iter_reconstruct(b)
            yield pp

        yield from iter_reconstruct(final)

    # Check object connection is exists
    if not obj.has_connection(connection):
        raise KeyError("Invalid connection name")
    # First connection
    oc = ObjectConnection.objects.filter(
        __raw__={"connection": {"$elemMatch": {"object": obj.id, "name": connection}}}
    ).first()
    if not oc:
        return None
    # Process starting connection
    tp = set(ProtocolVariant.get_by_code(p) for p in target_protocols)
    wave: Set[Object] = set()  # Search wave
    prev: Dict[PathItem, PathItem] = {}
    p0 = PathItem(obj=obj, connection=connection)
    for c in oc.connection:
        if c.object == obj and c.name == connection:
            continue
        r = get_action(c.object, c.name)
        if r == ConnAction.FOUND:
            # Found
            return [
                p0,
                PathItem(obj=c.object, connection=c.name),
            ]
        elif r == ConnAction.PASS:
            # Passable
            wave.add(c.object)
            prev[PathItem(obj=c.object, connection=c.name)] = p0
    if not wave:
        return None  # No suitable completion
    # Process waves
    seen: Set[Object] = {obj}  # Seen objects should never be present in wave
    while wave and max_depth > 0:
        new_wave: Set[Object] = set()  # Wave for the next step
        # Collapse the wave and build adjacency matrix
        neighbors: DefaultDict[Object, List[AdjItem]] = defaultdict(list)
        for oc in ObjectConnection.objects.filter(connection__object__in=list(wave)):
            for c1, c2 in permutations(oc.connection, 2):
                neighbors[c1.object] += [
                    AdjItem(local_name=c1.name, remote_object=c2.object, remote_name=c2.name)
                ]
        # Process the wave
        for co in wave:
            # Find incoming
            incoming: Optional[str] = None
            for adj in neighbors[co]:
                pi = PathItem(obj=co, connection=adj.local_name)
                if pi in prev:
                    incoming = adj.local_name
                    break
            if not incoming:
                # Object in wave, but we cannot remember how we'd reached here.
                raise RuntimeError("Teleportation detected")
            # Process candidates
            for adj in neighbors[co]:
                if adj.remote_object in seen:
                    continue  # Already been there, nothing interesting
                if adj.remote_object in wave:
                    continue  # Shortest path cannot slide across the edge of wave
                r = get_action(adj.remote_object, adj.remote_name)
                if r == ConnAction.PASS or r == ConnAction.FOUND:
                    # Connect internal slots, only if we're not returning back to the incoming
                    pi = PathItem(obj=co, connection=adj.local_name)
                    if adj.local_name != incoming:
                        prev[pi] = PathItem(obj=co, connection=incoming)
                    # Connect remote candidate
                    prev[PathItem(obj=adj.remote_object, connection=adj.remote_name)] = pi
                    if r == ConnAction.FOUND:
                        # Reconstruct path
                        return list(
                            iter_path(PathItem(obj=adj.remote_object, connection=adj.remote_name))
                        )
                    else:  # ConnAction.PASS
                        new_wave.add(adj.remote_object)
        seen |= wave
        wave = new_wave
        max_depth -= 1
    # Wave is stopped, no path
    return None
