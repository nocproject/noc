# ----------------------------------------------------------------------
# BaseTracer class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Iterable, Optional, List, Tuple
from dataclasses import dataclass
import logging
from itertools import count
import datetime

# Third-party modules
from bson import ObjectId

# NOC modules
from noc.inv.models.objectmodel import Crossing, ObjectModelConnection
from noc.inv.models.object import Object
from noc.inv.models.objectconnection import ObjectConnection
from noc.inv.models.techdomain import TechDomain
from noc.inv.models.channel import Channel
from noc.inv.models.endpoint import Endpoint as DBEndpoint
from noc.core.channel.types import ChannelKind, ChannelTopology
from noc.core.log import PrefixLoggerAdapter
from noc.core.resource import from_resource


@dataclass
class Endpoint(object):
    """ """

    object: Object
    name: str
    channel: Optional[Channel] = None

    def __hash__(self) -> int:
        return hash((str(self.object.id), self.name))

    def as_resource(self) -> str:
        return f"o:{self.object.id}:{self.name}"


@dataclass
class PathItem(object):
    object: Object
    input: Optional[str]
    output: Optional[str]
    input_discriminator: Optional[str] = None
    channel: Optional[Channel] = None
    output_object: Optional[Object] = None


class BaseTracer(object):
    name: str = "base"
    tech_domain: str
    kind: ChannelKind
    topology: ChannelTopology
    adhoc_bidirectional: bool = False

    def __init__(self):
        self.logger = PrefixLoggerAdapter(logging.getLogger("tracer"), self.name)

    @property
    def is_unidirectional(self) -> bool:
        """
        Check if topology is unidirectional.
        """
        return self.topology in (
            ChannelTopology.UP2P,
            ChannelTopology.UBUNCH,
            ChannelTopology.UP2MP,
        )

    @property
    def use_pairs(self) -> bool:
        """
        Check if pair numbers must be used
        """
        return self.topology in (ChannelTopology.BUNCH, ChannelTopology.UBUNCH)

    def iter_endpoints(self, obj: Object) -> Iterable[Endpoint]:
        """
        Iterate connections which can be served as endpoints.
        """
        return iter(())

    def iter_path(self, start: Endpoint) -> Iterable[PathItem]:
        """
        Iterate all intermediate points of path
        """
        return iter(())

    def trace_path(self, start: Endpoint) -> Optional[Endpoint]:
        """
        Trace path from starting endpoint to the end.

        Args:
            start: Starting endpoint

        Returns:
            ending endpoint, if possible, None otherwise
        """
        try:
            *_, last = self.iter_path(start)
        except ValueError:
            return None  # No path
        return Endpoint(object=last.object, name=last.output if last.output else last.input)

    def is_ad_hoc_available(self, obj: Object) -> bool:
        """
        Check if ad-hoc channel can be created.
        """
        self.logger.debug("Checking ad-hoc paths for %s", obj.name)
        for ep in self.iter_endpoints(obj):
            end = self.trace_path(ep)
            if end:
                self.logger.debug("Ad-hoc path found for %s", end.as_resource())
                if self.adhoc_bidirectional:
                    self.logger.debug("Tracing reverse path")
                    start = self.trace_path(end)
                    if start:
                        self.logger.debug("Reverse path found for %s", start.as_resource())
                        if ep.as_resource() == start.as_resource():
                            return True
                else:
                    return True
        self.logger.debug("No any ad-hoc paths found")
        return False

    @classmethod
    def iter_nested_objects(self, obj: Object) -> Iterable[Object]:
        """
        Iterate all nested objects.
        """
        # Get objects by hierarchy
        hier_ids: List[ObjectId] = obj.get_nested_ids()
        omap = {}
        for o in Object.objects.filter(id__in=hier_ids):
            omap[o.id] = o
            yield o
        # Find vertical
        wave = list(omap)
        while wave:
            new_wave = []
            for c in ObjectConnection.objects.filter(connection__object__in=wave):
                if len(c.connection) != 2:
                    continue  # @todo: Process later
                if c.connection[0].object.id in omap:
                    local = c.connection[0]
                    remote = c.connection[1]
                else:
                    local = c.connection[1]
                    remote = c.connection[0]
                if remote.object.id in omap:
                    continue  # Already processed
                mc = local.object.model.get_model_connection(local.name)
                if mc and mc.is_inner:
                    omap[remote.object.id] = remote.object
                    new_wave.append(remote.object)
                    yield remote.object
            wave = new_wave

    def get_peer(self, ep: Endpoint) -> Optional[Endpoint]:
        """
        Get connected peer.

        Pass through cables.

        Args:
            ep: Current endpoint

        Returns:
            Peer endpoint if found, None otherwise
        """
        self.logger.debug("Get peer for %s", ep)
        _, ro, rn = ep.object.get_p2p_connection(ep.name)
        if not ro:
            self.logger.debug("Not connected")
            return None
        if not ro.is_wire:
            self.logger.debug("Wire not found")
            return None
        # Pass through cross
        for out in ro.iter_cross(rn):
            # Get other side
            _, rro, rrn = ro.get_p2p_connection(out)
            if rro:
                oep = Endpoint(object=rro, name=rrn)
                self.logger.debug("Peer found: %s", oep)
                return oep
            break
        self.logger.debug("Broken cable")
        return None

    def iter_cross(self, obj: Object) -> Iterable[Crossing]:
        """
        Iterate all crossings
        """
        if obj.model.cross:
            yield from obj.model.cross
        if obj.cross:
            yield from obj.cross

    def validate_ad_hoc_channel(self, channel: Channel) -> None:
        """
        Check channel is valid for ad-hoc/creation, updating

        Args:
            channel: Channel to validate

        Raises:
            ValueError: on error
        """
        if channel.tech_domain.code != self.tech_domain:
            msg = f"Expecting tech_domain {self.tech_domain}, found {channel.tech_domain.code}"
            raise ValueError(msg)
        if channel.kind != self.kind.value:
            msg = f"Expecting {self.kind.value} kind, found {channel.kind}"
            raise ValueError(msg)
        if channel.topology != self.topology.value:
            msg = f"Expecting {self.topology.value}, found {channel.topology}"
            raise ValueError(msg)

    def create_ad_hoc_channel(self) -> Channel:
        """
        Create new ad-hoc channel instace
        """
        ch = Channel(
            tech_domain=TechDomain.get_by_code(self.tech_domain),
            name=f"Ad-hoc {self.name} {datetime.datetime.now().isoformat()}",
            description=f"Created by {self.name} tracer",
            kind=self.kind.value,
            topology=self.topology.value,
        )
        ch.save()
        return ch

    def sync_ad_hoc_channel(self, obj: Object) -> Tuple[Optional[Channel], str]:
        """
        Create or update ad-hoc channel.

        Args:
            obj: Starting object
            name: Proposed channel name

        Returns:
            Channel instance, message
        """

        def next_free_pair() -> Optional[int]:
            """
            Generate next free pair number
            """
            if not self.use_pairs:
                return None
            while True:
                pn = next(pair_count)
                if pn not in used_pairs:
                    return pn

        # Trace paths
        pairs = []
        resources = set()
        for sep in self.iter_endpoints(obj):
            eep = self.trace_path(sep)
            if not eep:
                continue
            pairs.append((sep, eep))
            resources.add(sep.as_resource())
            resources.add(eep.as_resource())
        # Find existing endpoints
        current_endpoints = {
            e.resource: e for e in DBEndpoint.objects.filter(resource__in=list(resources))
        }
        # Get channel or create new
        if current_endpoints:
            # Calculate number of channels
            cc = {x.channel for x in current_endpoints.values()}
            if len(cc) > 2:
                return None, "Multiple channels exists"
            channel = list(cc)[0]
            try:
                self.validate_ad_hoc_channel(channel)
            except ValueError as e:
                return None, str(e)
            used_pairs = {x.pair for x in current_endpoints.values() if x.pair}
        else:
            # Brand new channel
            channel = self.create_ad_hoc_channel()
            used_pairs = set()
        # Process endpoints
        pair_count = count(1)
        for sep, eep in pairs:
            start = current_endpoints.get(sep.as_resource())
            if not start:
                # Create start endpoint
                start = DBEndpoint(
                    channel=channel,
                    resource=sep.as_resource(),
                    is_root=self.is_unidirectional,
                    pair=next_free_pair() if self.use_pairs else None,
                )
                start.save()
            end = current_endpoints.get(eep.as_resource())
            if not end:
                end = DBEndpoint(
                    channel=channel,
                    resource=eep.as_resource(),
                    is_root=False,
                    pair=start.pair if self.use_pairs else None,
                )
                end.save()
        # @todo: Remove hanging endpoints
        if current_endpoints:
            return channel, "Channel updated"
        return channel, "Channel created"

    def is_connected(self, obj: Object, name: str) -> bool:
        """
        Check if connection is connected.

        Args:
            obj: Object instance
            name: connection name

        Returns:
            True: if object connected.
            False: if object is not connected
        """
        _, ro, _ = obj.get_p2p_connection(name)
        return bool(ro)

    def down(self, obj: Object, name: str) -> Optional[Object]:
        """
        Go down the connnection.

        Args:
            obj: Object instance.
            name: Connection name.

        Returns:
            Underlying object if found, none otherwise
        """
        _, ro, _ = obj.get_p2p_connection(name)
        return ro

    def up(self, obj: Object) -> Optional[Endpoint]:
        """
        Go to the parent object

        Args:
            obj: Object instance.
            name: Connection name.

        Returns:
            Underlying object if found, none otherwise
        """
        for _, ro, rname in obj.iter_outer_connections():
            return Endpoint(object=ro, name=rname)
        return None

    def get_connection(self, obj: Object, name: str) -> Optional[ObjectModelConnection]:
        """
        Get connection by name.
        """
        for c in obj.model.connections:
            if c.name == name:
                return c
        return None

    def pass_channel(self, ep: Endpoint) -> Optional[Endpoint]:
        """
        Pass through the channel.

        Pass through the channel if endpoint.

        Args:
            ep: Endpoint

        Returns:
            Channel exit point, if passed.
        """
        e = DBEndpoint.objects.filter(resource=ep.as_resource()).first()
        if not e:
            return None
        ch = e.channel
        if ch.topology == ChannelTopology.UBUNCH.value:
            if not e.is_root:
                return False  # Opposite direction
            endpoints = list(DBEndpoint.objects.filter(channel=ch.id, pair=e.pair, is_root=False))
            if len(endpoints) != 1:
                return None  # Broken channel
            e = endpoints[0]
            o, n = from_resource(e.resource)
            return Endpoint(object=o, name=n, channel=ch)
        msg = f"Topology {ch.topology} is not supported"
        raise NotImplementedError(msg)
