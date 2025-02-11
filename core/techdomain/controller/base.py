# ----------------------------------------------------------------------
# BaseController class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Iterable, Any
from dataclasses import dataclass
import logging
from enum import Enum
from collections import defaultdict

# NOC modules
from noc.inv.models.objectmodel import ObjectModelConnection
from noc.inv.models.object import Object
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
    channel: Channel | None = None

    def __hash__(self) -> int:
        return hash((str(self.object.id), self.name))

    def as_resource(self) -> str:
        if self.name:
            return f"o:{self.object.id}:{self.name}"
        return f"o:{self.object.id}"

    @classmethod
    def from_resource(cls, res: str) -> "Endpoint":
        o, n = from_resource(res)
        return Endpoint(object=o, name=n)

    @property
    def label(self) -> str:
        """Human-friendly label."""
        r = self.object.get_local_name_path(True)
        r.append(self.name)
        return " > ".join(r)

    @property
    def is_qualified(self) -> bool:
        """Check if endpoint has slot name."""
        return bool(self.name)


class ParamType(Enum):
    STRING = "string"


@dataclass
class Choice(object):
    id: str
    label: str

    def to_json(self) -> dict[str, str]:
        return {
            "id": self.id,
            "label": self.label,
        }


@dataclass
class Param(object):
    name: str
    type: ParamType
    value: str | None
    label: str | None = None
    choices: list[Choice] | None = None
    readonly: bool = False
    required: bool = True

    def to_json(self) -> dict[str, Any]:
        r: dict[str, Any] = {
            "name": self.name,
            "type": self.type.value,
            "label": self.label or self.name,
            "value": self.value,
            "readonly": self.readonly,
            "required": self.required,
        }
        if self.choices:
            r["choices"] = [c.to_json() for c in self.choices]
        return r


class Constraint(object):
    """
    Channel costraint.

    Represents a single restriction on channel.

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


class ProtocolConstraint(Constraint):
    """
    Protocol restrictions.

    Represents single protocol.

    Args:
        proto: Protocol name.
    """

    def __init__(self: "ProtocolConstraint", proto: str) -> None:
        super().__init__()
        self._proto = proto

    def __str__(self: "ProtocolConstraint") -> str:
        return self._proto

    def __eq__(self, value: object) -> bool:
        return isinstance(value, ProtocolConstraint) and self._proto == value._proto

    @property
    def protocol(self: "ProtocolConstraint") -> str:
        return self._proto


class LambdaConstraint(Constraint):
    """
    Optical lambda.

    Represented by central frequency and width.

    Args:
        freq: Central frequency in MHz.
        width: Channel width in MHz.
    """

    def __init__(self: "LambdaConstraint", freq: int, width: int) -> None:
        self._freq = freq
        self._width = width

    def __str__(self: "LambdaConstraint") -> str:
        return f"{self._freq}-{self._width}"

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, LambdaConstraint)
            and self._freq == value._freq
            and self._width == value._width
        )

    @property
    def min_freq(self: "LambdaConstraint") -> int:
        """Minimal frequency in GHz."""
        return self._freq - self._width // 2

    @property
    def max_freq(self: "LambdaConstraint") -> int:
        """Maximal frequency in GHz."""
        return self._freq + self._width // 2

    @classmethod
    def from_discriminator(cls: "type[LambdaConstraint]", v: str) -> "LambdaConstraint":
        """Create constraint from lambda discriminator."""
        freq, width = v[8:].split("-")
        return LambdaConstraint(int(freq) * 1_000, int(width) * 1_000)

    @property
    def discriminator(self: "LambdaConstraint") -> str:
        """Convert to discriminator."""
        return f"lambda::{self._freq // 1_000}-{self._width // 1_000}"


class ConstraintSet(object):
    """
    Set of restrictions.
    """

    def __init__(self: "ConstraintSet") -> None:
        self._data: defaultdict[type[Constraint], list[Constraint]] = defaultdict(list)

    def get(self: "ConstraintSet", item: type[Constraint]) -> list[Constraint] | None:
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
    def from_iter(cls: "type[ConstraintSet]", iter: Iterable[Constraint]) -> "ConstraintSet":
        r = cls()
        for item in iter:
            r.extend(item)
        return r

    def __iter__(self: "ConstraintSet") -> Iterable[Constraint]:
        for items in self._data.values():
            yield from items

    def extend(self: "ConstraintSet", item: Constraint) -> None:
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

        def iter_intersect(left: list[Constraint], right: list[Constraint]) -> Iterable[Constraint]:
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


@dataclass
class PathItem(object):
    object: Object
    input: str | None
    output: str | None
    input_discriminator: str | None = None
    channel: Channel | None = None
    output_object: Object | None = None


class BaseController(object):
    name: str = "base"
    tech_domain: str
    kind: ChannelKind
    topology: ChannelTopology
    adhoc_bidirectional: bool = False
    # True - iter_adhoc_endpoints will return entryponts
    # False - return whole object
    adhoc_endpoints: bool = False

    def __init__(self):
        self.logger = PrefixLoggerAdapter(logging.getLogger("controller"), self.name)
        self.constraints = ConstraintSet()

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

    def reset_constraints(self) -> None:
        """
        Reset current constraints.
        """
        self.constraints = ConstraintSet()

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

    def trace_path(self, start: Endpoint) -> Endpoint | None:
        """
        Trace path from starting endpoint to the end.

        Reset controller's constraints.

        Args:
            start: Starting endpoint

        Returns:
            ending endpoint, if possible, None otherwise
        """
        self.reset_constraints()
        try:
            *_, last = self.iter_path(start)
        except ValueError:
            return None  # No path
        return Endpoint(object=last.object, name=last.output if last.output else last.input)

    def iter_adhoc_endpoints(
        self, obj: Object
    ) -> Iterable[tuple[Endpoint, Endpoint, ConstraintSet]]:
        """
        Iterate endpoints suitable to create a channel.

        Returns:
            Tuple of starting and ending endpoints.
        """
        for ep in self.iter_endpoints(obj):
            # Trace forward path and get path's constraints
            end = self.trace_path(ep)
            if not end:
                continue  # Untraceable
            fwd_constraints = self.constraints
            if self.adhoc_bidirectional:
                # Trace back
                start = self.trace_path(end)
                if not start:
                    continue
                back_constraints = self.constraints
                # Returned back
                if ep.as_resource() == start.as_resource():
                    r_constraints = fwd_constraints.intersect(back_constraints)
                    if not r_constraints:
                        continue  # Unimplementable
                    if self.adhoc_endpoints:
                        yield ep, end, r_constraints
                    else:
                        # Whole object
                        yield Endpoint(object=obj, name=""), Endpoint(
                            object=end.object, name=""
                        ), r_constraints
                        return
            elif self.adhoc_endpoints:
                yield ep, end, fwd_constraints
            else:
                # Whole object
                yield Endpoint(object=obj, name=""), Endpoint(
                    object=end.object, name=""
                ), fwd_constraints
                return

    def get_peer(self, ep: Endpoint) -> Endpoint | None:
        """
        Get connected peer.

        Pass through cables.

        Args:
            ep: Current endpoint

        Returns:
            Peer endpoint if found, None otherwise
        """
        self.logger.info("Get peer for %s", ep.label)
        _, ro, rn = ep.object.get_p2p_connection(ep.name)
        if not ro:
            self.logger.info("Not connected")
            return None
        if not ro.is_wire:
            self.logger.info("Wire not found")
            return None
        # Pass through cross
        for oc in ro.iter_cross(rn):
            # Get other side
            _, rro, rrn = ro.get_p2p_connection(oc.output)
            if rro:
                oep = Endpoint(object=rro, name=rrn)
                self.logger.info("Peer found: %s", oep.label)
                return oep
            break
        self.logger.info("Broken cable: %s", ro.model.name)
        return None

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

    def create_ad_hoc_channel(self, name: str, discriminator: str | None = None) -> Channel:
        """
        Create new ad-hoc channel instace
        """
        ch = Channel(
            tech_domain=TechDomain.get_by_code(self.tech_domain),
            name=name,
            description=f"Created by {self.name} controller",
            kind=self.kind.value,
            topology=self.topology.value,
            discriminator=discriminator,
            controller=self.name,
        )
        ch.save()
        return ch

    def sync_ad_hoc_channel(
        self,
        name: str,
        ep: Endpoint,
        channel: Channel | None = None,
        dry_run: bool = False,
        **kwargs: Any,
    ) -> tuple[Channel | None, str]:
        """
        Create or update ad-hoc channel.

        Args:
            name: Channel name.
            ep: Starting endpoint.
            channel: Channel instance when updating.
            dry_run: Run jobs in dry_run mode.

        Returns:
            Channel instance, message
        """
        raise NotImplementedError

    def get_ad_hoc_params(self, endpoints: list[Endpoint]) -> list[Param] | None:
        """
        Get possible channel parameters.

        Args:
            endpoints: List of endpoints.

        Returns:
            List of params or None
        """
        return None

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

    def down(self, obj: Object, name: str) -> Object | None:
        """
        Go down the connnection.

        Args:
            obj: Object instance.
            name: Connection name.

        Returns:
            Underlying object if found, none otherwise
        """
        return Object.objects.filter(parent=obj.id, parent_connection=name).first()

    def up(self, obj: Object) -> Endpoint | None:
        """
        Go to the parent object

        Args:
            obj: Object instance.
            name: Connection name.

        Returns:
            Underlying object if found, none otherwise
        """
        return Endpoint(object=obj.parent, name=obj.parent_connection)

    def get_connection(self, obj: Object, name: str) -> ObjectModelConnection | None:
        """
        Get connection by name.
        """
        for c in obj.model.connections:
            if c.name == name:
                return c
        return None

    def pass_channel(self, ep: Endpoint) -> Endpoint | None:
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
        if ch.topology == ChannelTopology.P2P.value:
            endpoints = list(DBEndpoint.objects.filter(channel=ch.id))
            if len(endpoints) != 2:
                return None  # No valid channel
            eps = [x for x in endpoints if x.resource != ep.as_resource()]
            o, n = from_resource(eps[0].resource)
            return Endpoint(object=o, name=n, channel=ch)
        if ch.topology == ChannelTopology.UBUNCH.value:
            if not e.is_root:
                return None  # Opposite direction
            endpoints = list(DBEndpoint.objects.filter(channel=ch.id, pair=e.pair, is_root=False))
            if len(endpoints) != 1:
                return None  # Broken channel
            e = endpoints[0]
            o, n = from_resource(e.resource)
            return Endpoint(object=o, name=n, channel=ch)
        msg = f"Topology {ch.topology} is not supported"
        raise NotImplementedError(msg)

    @classmethod
    def update_name(cls, channel: Channel, name: str) -> None:
        """
        Update channel name if necessary.

        Args:
            channel: Channel reference.
            name: Channel name.
        """
        if channel.name != name:
            channel.name = name
            channel.save()

    @classmethod
    def to_params(cls: "type[BaseController]", constraints: ConstraintSet) -> list[Param]:
        """
        Convert constraints to list of params.
        """
        return []
