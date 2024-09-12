# ---------------------------------------------------------------------
# Object model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import operator
from dataclasses import dataclass
from threading import Lock
from typing import Optional, Any, Dict, Union, List, Set, Iterator
import warnings

# Third-party modules
from bson import ObjectId
from pymongo import ReadPreference
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    ListField,
    PointField,
    LongField,
    EmbeddedDocumentField,
    EmbeddedDocumentListField,
    DynamicField,
    ReferenceField,
    BooleanField,
    DateTimeField,
)
from mongoengine import signals
from mongoengine.queryset.queryset import QuerySet
import cachetools
from typing import Iterable, Tuple

# NOC modules
from noc.gis.models.layer import Layer, DEFAULT_ZOOM
from noc.core.mongo.fields import PlainReferenceField
from noc.core.copy import deep_merge
from noc.core.middleware.tls import get_user
from noc.core.gridvcs.manager import GridVCSField
from noc.core.defer import call_later
from noc.core.model.decorator import on_save, on_delete_check
from noc.core.bi.decorator import bi_sync
from noc.core.change.decorator import change
from noc.core.topology.types import TopologyNode
from noc.core.discriminator import discriminator
from noc.core.confdb.collator.typing import PortItem, PathItem
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.label import Label
from noc.core.comp import smart_text
from noc.config import config
from noc.pm.models.agent import Agent
from noc.cm.models.configurationscope import ConfigurationScope
from noc.cm.models.configurationparam import ConfigurationParam, ParamData, ScopeVariant
from noc.inv.models.technology import Technology
from noc.core.deprecations import RemovedInNOC2501Warning
from .objectmodel import ObjectModel, Crossing
from .modelinterface import ModelInterface
from .objectlog import ObjectLog
from .error import ConnectionError, ModelDataError
from .protocol import ProtocolVariant

id_lock = Lock()
_path_cache = cachetools.TTLCache(maxsize=1000, ttl=60)


@dataclass(frozen=True)
class ConnectionData(object):
    name: str
    protocols: List[ProtocolVariant]
    data: Dict[str, Any]
    cross: Optional[str] = None
    group: Optional[str] = None
    interface_name: Optional[str] = None


class ObjectConnectionData(EmbeddedDocument):
    # Connection name (from model)
    name = StringField()
    # Bound interface
    interface_name = StringField()

    def __str__(self):
        return self.name


class ObjectAttr(EmbeddedDocument):
    interface = StringField()
    attr = StringField()
    value = DynamicField()
    scope = StringField()

    def __str__(self):
        if self.scope:
            return "%s.%s@%s = %s" % (self.interface, self.attr, self.scope, self.value)
        return "%s.%s = %s" % (self.interface, self.attr, self.value)


class ObjectConfigurationScope(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    scope: "ConfigurationScope" = PlainReferenceField(ConfigurationScope, required=True)
    value: str = StringField(required=False)

    def __str__(self):
        return f"@{self.code}"

    @property
    def code(self) -> str:
        if not self.value:
            return self.scope.name
        return f"{self.scope.name}::{self.value}"

    def __hash__(self):
        return hash(self.code)

    def __eq__(self, other) -> bool:
        if self.scope.id != other.scope.id:
            return False
        if not self.value:
            return True
        return self.value == other.value

    @classmethod
    def from_code(cls, code: str) -> List["ObjectConfigurationScope"]:
        """
        Getting ObjectConfigurationScope from code.
        :param code: Format @code1@code2...
        """
        r = []
        for s in code[1:].split("@"):
            sv = ScopeVariant.from_code(s)
            r.append(ObjectConfigurationScope(scope=sv.scope, value=sv.value))
        return r


class ObjectConfigurationData(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    param: "ConfigurationParam" = PlainReferenceField(ConfigurationParam, required=True)
    value = DynamicField()
    is_dirty = BooleanField(default=False)
    is_conflicted = BooleanField(default=False)
    conflicted_value = DynamicField(required=False)
    last_seen = DateTimeField()
    # Scope Code
    contexts: Optional[List["ObjectConfigurationScope"]] = EmbeddedDocumentListField(
        ObjectConfigurationScope, required=False
    )

    def __str__(self):
        if self.contexts:
            return f"{self.param.code}{self.scope} = {self.value}"
        return f"{self.param.code} = {self.value}"

    @property
    def scope(self) -> str:
        return "".join(f"@{s.code}" for s in self.contexts)


class ObjectQuerySet(QuerySet):
    """Fix Object.container usage"""

    def __call__(self, **kwargs):
        legacy = [k for k in kwargs if k.startswith("container")]
        if legacy:
            # Rewrite container queryes
            warnings.warn(
                "Object.container is deprecated and will be removed in NOC 25.1",
                RemovedInNOC2501Warning,
            )
            for q in legacy:
                kwargs[f"parent{q[9:]}"] = kwargs.pop(q)
            kwargs["parent_connection__exists"] = False
        return super().__call__(**kwargs)


@Label.model
@bi_sync
@on_save
@change
@on_delete_check(
    check=[
        ("sa.ManagedObject", "container"),
        ("inv.CoveredObject", "object"),
        ("inv.Object", "parent"),
    ],
    delete=[("inv.Sensor", "object")],
)
class Object(Document):
    """
    Inventory object
    """

    meta = {
        "collection": "noc.objects",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            "data",
            ("parent", "parent_connection"),
            ("name", "parent"),
            ("data.interface", "data.attr", "data.value"),
            "labels",
            "effective_labels",
        ],
        "queryset_class": ObjectQuerySet,
    }

    name = StringField()
    model: "ObjectModel" = PlainReferenceField(ObjectModel)
    data: List["ObjectAttr"] = ListField(EmbeddedDocumentField(ObjectAttr))
    parent: Optional["Object"] = PlainReferenceField("self", required=False)
    parent_connection = StringField(required=False)
    additional_connections = ListField(StringField(), required=False)
    comment = GridVCSField("object_comment")
    # Configuration Param
    cfg_data: List["ObjectConfigurationData"] = ListField(
        EmbeddedDocumentField(ObjectConfigurationData)
    )
    # Map
    layer: Optional["Layer"] = PlainReferenceField(Layer)
    point = PointField(auto_index=True)
    # Additional connection data
    connections: List["ObjectConnectionData"] = ListField(
        EmbeddedDocumentField(ObjectConnectionData)
    )
    # Dynamic crossings
    cross: List[Crossing] = ListField(EmbeddedDocumentField(Crossing))
    # Labels
    labels = ListField(StringField())
    effective_labels = ListField(StringField())
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = ReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Object id in BI
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

    REBUILD_CONNECTIONS = ["links", "conduits"]

    def __str__(self):
        return smart_text(self.name or self.id)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["Object"]:
        return Object.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["Object"]:
        return Object.objects.filter(bi_id=bi_id).first()

    def resource_label(self) -> str:
        """
        Generate resource label.
        """
        return " > ".join(self.get_local_name_path(True))

    def iter_changed_datastream(self, changed_fields=None):
        if config.datastream.enable_managedobject:
            if self.data and self.get_data("management", "managed_object"):
                yield "managedobject", self.get_data("management", "managed_object")
            else:
                o = self.get_box()
                if o.data and o.get_data("management", "managed_object"):
                    yield "managedobject", o.get_data("management", "managed_object")

    def clean(self):
        self.set_point()

    def set_point(self):
        from noc.gis.map import map

        # Reset previous data
        self.layer = None
        self.point = None
        # Get points
        x, y, srid = self.get_data_tuple("geopoint", ("x", "y", "srid"))
        if x is None or y is None:
            return  # No point data
        # Get layer
        layer_code = self.model.get_data("geopoint", "layer")
        if not layer_code:
            return
        layer = Layer.get_by_code(layer_code)
        if not layer:
            return
        # Update actual data
        self.layer = layer
        self.point = map.get_db_point(x, y, srid=srid)

    def on_save(self):
        def get_coordless_objects(o):
            r = {str(o.id)}
            for co in Object.objects.filter(parent=o.id):
                cx, cy = co.get_data_tuple("geopoint", ("x", "y"))
                if cx is None and cy is None:
                    r |= get_coordless_objects(co)
            return r

        x, y = self.get_data_tuple("geopoint", ("x", "y"))
        if x is not None and y is not None:
            # Rebuild connection layers
            for ct in self.REBUILD_CONNECTIONS:
                for c, _, _ in self.get_genderless_connections(ct):
                    c.save()
            # Update nested objects
            from noc.sa.models.managedobject import ManagedObject

            mos = get_coordless_objects(self)
            if mos:
                ManagedObject.objects.filter(container__in=mos).update(
                    x=x, y=y, default_zoom=self.layer.default_zoom if self.layer else DEFAULT_ZOOM
                )
        if self._created:
            self.refresh_pop_links()
        # Changed parent
        elif hasattr(self, "_changed_fields") and "parent" in self._changed_fields:
            # Old pop
            old_parent_id = getattr(self, "_old_parent", None)
            old_pop = None
            if old_parent_id:
                c = Object.get_by_id(old_parent_id)
                while c:
                    if c.get_data("pop", "level"):
                        old_pop = c
                        break
                    c = c.parent
            # New pop
            new_pop = self.get_pop()
            # Check if pop moved
            if old_pop != new_pop:
                if old_pop:
                    old_pop.update_pop_links()
                if new_pop:
                    new_pop.update_pop_links()

    @cachetools.cached(_path_cache, key=lambda x: str(x.id), lock=id_lock)
    def get_path(self) -> List[str]:
        """
        Returns list of parent segment ids
        :return:
        """
        if self.parent:
            return self.parent.get_path() + [self.id]
        return [self.id]

    @property
    def level(self) -> int:
        """
        Return level
        :return:
        """
        if not self.parent:
            return 0
        return len(self.get_path()) - 1  # self

    @property
    def has_children(self) -> bool:
        return bool(Object.objects.filter(parent=self.id).first())

    @property
    def is_wire(self) -> bool:
        # @todo: Replace with proper implementation
        return bool(self.model.get_data("length", "length"))

    @property
    def is_generic_transceiver(self) -> bool:
        """
        Check object create by Template Model
        """
        return self.model.name.startswith("Generic | Transceiver") or self.model.name.startswith(
            "NoName | Transceiver"
        )

    @property
    def is_generic(self) -> bool:
        """
        Object is Generic
        """
        return self.model.vendor.name == "Generic" or self.model.vendor.name == "NoName"

    @property
    def is_point(self) -> bool:
        """
        Check if object has coordinates
        """
        return (
            self.get_data("geopoint", "x") is not None
            and self.get_data("geopoint", "y") is not None
        )

    @property
    def is_container(self) -> bool:
        """
        Check if object is container
        """
        return bool(self.get_data("container", "container"))

    @property
    def is_rack(self) -> bool:
        """Check if object is rack."""
        return bool(self.get_data("rack", "units"))

    @property
    def is_rackmount(self) -> bool:
        """Check if object is rack-mountable"""
        return bool(self.get_data("rackmount", "units"))

    def get_nested_ids(self):
        """
        Return id of this and all nested object
        :return:
        """
        # $graphLookup hits 100Mb memory limit. Do not use it
        seen = {self.id}
        wave = {self.id}
        max_level = 7
        coll = Object._get_collection()
        for _ in range(max_level):
            # Get next wave
            wave = (
                set(d["_id"] for d in coll.find({"parent": {"$in": list(wave)}}, {"_id": 1})) - seen
            )
            if not wave:
                break
            seen |= wave
        return list(seen)

    def get_data(
        self,
        interface: str,
        key: str,
        scope: Optional[str] = None,
        connection: Optional[str] = None,
        protocol: Optional[str] = None,
    ) -> Any:
        attr = ModelInterface.get_interface_attr(interface, key)
        if attr.is_const:
            # Lookup model
            v = self.model.get_data(interface, key)
            if v is not None:
                return v
        for item in self.data:
            if item.interface == interface and item.attr == key:
                if not scope or item.scope == scope:
                    return item.value
        if attr.is_const:
            # Lookup model
            v = self.model.get_data(interface, key)
            if v is not None:
                return v
        return None

    def get_data_dict(
        self, interface: str, keys: Iterable, scope: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get multiple keys from single interface. Returns dict with values for every given key.
        If key is missed, return None value

        :param interface:
        :param keys: Iterable contains key names
        :param scope:
        :return:
        """
        kset = set(keys)
        r = {k: None for k in kset}
        for item in self.data:
            if item.interface == interface and item.attr in kset:
                if not scope or item.scope == scope:
                    r[item.attr] = item.value
        return r

    def get_data_tuple(
        self, interface: str, keys: Union[List, Tuple], scope: Optional[str] = None
    ) -> Tuple[Any, ...]:
        """
        Get multiple keys from single interface. Returns tuple with values for every given key.
        If key is missed, return None value

        :param interface:
        :param keys: List or tuple with key names
        :param scope:
        :return:
        """
        r = self.get_data_dict(interface, keys, scope)
        return tuple(r.get(k) for k in keys)

    def get_effective_data(self) -> List[ObjectAttr]:
        """
        Return effective object data, including the model's defaults
        :return:
        """
        seen: Set[Tuple[str, str, str]] = set()  # (interface, attr, scope
        r: List[ObjectAttr] = []
        # Object attributes
        for item in self.data:
            k = (item.interface, item.attr, item.scope or "")
            if k in seen:
                continue
            r += [item]
            seen.add(k)
        # Model attributes
        for item in self.model.data:
            k = (item.interface, item.attr, "")
            if k in seen:
                continue
            r += [ObjectAttr(interface=item.interface, attr=item.attr, scope="", value=item.value)]
            seen.add(k)
        # Sort according to interface
        sorting_keys: Dict[str, str] = {}
        for ni, i in enumerate(sorted(set(x[0] for x in seen))):
            mi = ModelInterface.get_by_name(i)
            if not mi:
                continue
            for na, a in enumerate(mi.attrs):
                sorting_keys["%s.%s" % (i, a.name)] = "%06d.%06d" % (ni, na)
        # Return sorted result
        return list(
            sorted(
                r,
                key=lambda oa: "%s.%s"
                % (sorting_keys.get("%s.%s" % (oa.interface, oa.attr), "999999.999999"), oa.scope),
            )
        )

    def set_data(self, interface: str, key: str, value: Any, scope: Optional[str] = None) -> None:
        attr = ModelInterface.get_interface_attr(interface, key)
        if attr.is_const:
            raise ModelDataError("Cannot set read-only value")
        value = attr._clean(value)
        for item in self.data:
            if item.interface == interface and item.attr == key:
                if not scope or item.scope == scope:
                    item.value = value
                    break
        else:
            # Insert new item
            self.data += [
                ObjectAttr(interface=interface, attr=attr.name, value=value, scope=scope or "")
            ]

    def reset_data(
        self, interface: str, key: Union[str, Iterable], scope: Optional[str] = None
    ) -> None:
        if isinstance(key, str):
            kset = {key}
        else:
            kset = set(key)
        v = [ModelInterface.get_interface_attr(interface, k).is_const for k in kset]
        if any(v):
            raise ModelDataError("Cannot reset read-only value")
        self.data = [
            item
            for item in self.data
            if item.interface != interface
            or (scope and item.scope != scope)
            or item.attr not in kset
        ]

    def has_cfg_scope(self, param: ConfigurationParam, scope: str) -> bool:
        """
        Check Configuration Scope exists on Object
        """
        return True

    def get_cfg_data(self, param: "ConfigurationParam", scope: Optional[str] = None) -> Any:
        """
        Getting Configuration Param Data. Scope - scope string
        """
        # Check Required Slot
        # if param.has_scopes(scope) and not scope:
        #     raise ValueError("Required Scope")
        scope = ConfigurationParam.clean_scope(param, scope)
        for item in self.cfg_data:
            if item.param == param:
                if not scope or item.scope == scope:
                    return item.value
        return None

    def set_cfg_data(
        self,
        param: "ConfigurationParam",
        value: Any,
        scope: Optional[str] = None,
        is_conflicted: bool = False,
        is_dirty: bool = False,
    ) -> None:
        """
        Set ConfigurationParam value, and check is_dirty for provisioning
        @todo check is_dirty provisioned, when reset (remove)?
        @todo Catch lock for protect when provisioned, is_dirty ?
        :param param: Changed Configured Param
        :param value: Param Value
        :param scope: Param scope
        :param is_conflicted: Param conflicted with current
        :param is_dirty: Param is dirty and needed provisioned
        """
        scope = ConfigurationParam.clean_scope(param, scope)
        schema = param.get_schema(self)
        # value = param.clean(value)
        for item in self.cfg_data:
            if item.param == param:
                if not scope or item.scope == scope:
                    item.value = schema.clean(value)
                    break
        else:
            # Insert new item
            self.cfg_data += [
                ObjectConfigurationData(
                    param=param,
                    value=value,
                    is_dirty=is_dirty,
                    contexts=ObjectConfigurationScope.from_code(scope),
                )
            ]

    def reset_cfg_data(
        self, param: Union["ConfigurationParam", List["ConfigurationParam"]], scope: Optional[str]
    ):
        """
        Remove Configuration Data for param from scope
        :param param: List param for reset
        :param scope: Configuration Scope from removed
        """
        if not isinstance(param, list):
            param = [param]
        r = []
        for cd in self.cfg_data:
            scope = ConfigurationParam.clean_scope(cd.param, scope)
            if cd.param in param and cd.scope == scope:
                continue
            r.append(cd)
        self.cfg_data = r

    def reset_cfg_scopes(self, scopes: List[str]):
        """
        Remove all Configuration Param for scopes
        :param: scopes list
        """
        self.cfg_data = [cd for cd in self.cfg_data if cd.scope not in scopes]

    def get_effective_cfg_params(self) -> List["ParamData"]:
        """
        Get all objects param with schema
        """
        # Getting param data
        param_data: Dict[Tuple[str, str], Any] = {}
        for d in self.cfg_data:
            param_data[(d.param.code, d.scope)] = d.value
        r: List["ParamData"] = []
        seen: Set[Tuple[str, str]] = set()
        if not self.model.configuration_rule:
            return r
        # Processed configurations param
        for pr in self.model.configuration_rule.param_rules:
            if not pr.param.has_required_scopes or pr.param.is_common:
                if (
                    pr.dependency_param
                    and self.get_cfg_data(pr.dependency_param) not in pr.dependency_param_values
                ):
                    continue
                schema = pr.param.get_schema(self)
                if pr.choices:
                    schema.choices = pr.choices
                r += [
                    ParamData(
                        code=pr.param.code,
                        scopes=[],
                        schema=schema,
                        value=param_data.pop((pr.param.code, ""), None),
                    )
                ]
                continue
            for scope in self.iter_configuration_scopes(pr.param):
                if (pr.param.code, scope.code) in seen:
                    continue
                if (
                    pr.dependency_param
                    and self.get_cfg_data(pr.dependency_param, scope.code)
                    not in pr.dependency_param_values
                ):
                    continue
                if pr.scope and pr.scope != scope.scope:
                    continue
                schema = pr.param.get_schema(self)
                # Getting param from connection model (for transceiver)
                if pr.choices:
                    schema.choices = pr.choices
                r += [
                    ParamData(
                        code=pr.param.code,
                        scopes=[scope],
                        schema=schema,
                        value=param_data.pop((pr.param.name, scope.code), None),
                    )
                ]
                seen.add((pr.param.code, scope.code))
        for key, value in param_data.items():
            param, *scopes = key
            param = ConfigurationParam.get_by_code(param)
            r += [
                ParamData(
                    code=param.code,
                    scopes=[ScopeVariant.from_code(s) for s in scopes if s],
                    schema=param.get_schema(self),
                    value=value,
                )
            ]
        # Add from data
        return r

    def iter_configuration_scopes(self, param: "ConfigurationParam") -> Iterable["ScopeVariant"]:
        for c in self.model.connections:
            scope = self.model.configuration_rule.get_scope(param, c)
            if not scope or not param.has_scope(scope.name) or scope.is_common:
                continue
            yield ScopeVariant(scope=scope, value=c.name)

    def get_effective_connection_data(self, name) -> ConnectionData:
        """
        Return effective connection data
        :return:
        """
        c = self.model.get_model_connection(name)
        if c is None:
            raise ConnectionError("Local connection not found: %s" % name)
        return ConnectionData(
            c.name,
            protocols=[ProtocolVariant.get_by_code(p.code) for p in c.protocols],
            data={},
            cross=c.cross_direction,
            group=c.group,
        )

    def get_crossing_proposals(
        self, name: str, to_name: Optional[str] = None
    ) -> List[Tuple[str, List[str]]]:
        """
        Return possible connections for connection name
        as (connection name, discriminators)
        * Getting proto (not compared proto because it's internal connect)
        * Getting discriminators
        * Iterable over compatible connections
        * Return connections and discriminators
        :param name: Connection name
        :param to_name: Other side connection
        :return:
        """
        lc = self.get_effective_connection_data(name)
        r = []
        # Exclude crossing
        for c in self.model.connections:
            if c.name == lc.name or (to_name and c.name != to_name) or c.composite:
                # Same
                continue
            c = self.get_effective_connection_data(c.name)
            if not c.cross or c.cross == lc.cross:
                continue
            elif lc.group != c.group:
                continue
            # Check protocols
            protocols, discriminators = [], []
            for lp in lc.protocols:
                for p in c.protocols:
                    pd = p.get_discriminator()
                    lpd = lp.get_discriminator()
                    if not pd and not lpd:
                        # Not supported discriminators
                        protocols.append(p)
                        continue
                    elif not pd or not lpd:
                        # Not supported discriminators
                        continue
                    # remove discriminators from crossing
                    if c.cross == "o":
                        d = pd.get_crossing_proposals(lpd)
                    else:
                        d = lpd.get_crossing_proposals(pd)
                    if not d:
                        continue
                    discriminators += d
                    protocols.append(p)
            if c.protocols and not protocols:
                continue
            # Check discriminators
            r.append((c.name, discriminators))
        return r

    def iter_connection_proposals(
        self,
        name: str,
        ro: "ObjectModel",
        remote_name: Optional[str] = None,
        use_cable: bool = False,
    ) -> Iterable[Tuple[Optional["ObjectModel"], str]]:
        """
        Iterate possible connections.
        """
        for model_id, c_name in self.model.iter_connection_proposals(name):
            if use_cable:
                model = ObjectModel.get_by_id(model_id)
                if bool(model.get_data("length", "length")):
                    # Wired, Multiple Cable?
                    yield model, c_name
            elif remote_name and c_name != remote_name:
                continue
            elif ro and ro.id == model_id:
                yield None, c_name

    def has_connection(self, name: str) -> bool:
        """
        Check if object has connection.
        """
        return self.model.has_connection(name)

    def get_p2p_connection(
        self, name: str
    ) -> Tuple[Optional[Any], Optional["Object"], Optional[str]]:
        """
        Get neighbor for p2p connection (s and mf types)
        Returns connection, remote object, remote connection or
        None, None, None
        """
        from .objectconnection import ObjectConnection, ObjectConnectionItem

        c = ObjectConnection.objects.filter(
            __raw__={"connection": {"$elemMatch": {"object": self.id, "name": name}}}
        ).first()
        if c:
            for x in c.connection:
                if x.object.id != self.id:
                    return c, x.object, x.name
        else:
            # Emulate legacy code
            # Will be removed in NOC 25.1
            mc = self.model.get_model_connection(name)
            if mc and mc.is_outer:
                warnings.warn(
                    "Object.get_p2p_connection for outer connections is deprecated "
                    "and will be removed in NOC 25.1",
                    RemovedInNOC2501Warning,
                )
                if not self.parent or not self.parent_connection:
                    return None, None, None
                c = ObjectConnection(
                    connection=[
                        ObjectConnectionItem(object=self, name=name),
                        ObjectConnectionItem(object=self.parent, name=self.parent_connection),
                    ]
                )
                return c, self.parent, self.parent_connection
            elif mc and mc.is_inner:
                warnings.warn(
                    "Object.get_p2p_connection for inner connections is deprecated "
                    "and will be removed in NOC 25.1",
                    RemovedInNOC2501Warning,
                )
                child = Object.objects.filter(parent=self.id, parent_connection=name).first()
                if child:
                    o_name = child.model.get_outer().name
                    c = ObjectConnection(
                        connection=[
                            ObjectConnectionItem(object=self, name=name),
                            ObjectConnectionItem(object=child, name=o_name),
                        ]
                    )
                    return c, child, o_name
        # Strange things happen
        return None, None, None

    def get_genderless_connections(self, name: str) -> List[Tuple[Any, "Object", str]]:
        """
        Get genderless connections
        """
        from .objectconnection import ObjectConnection

        r = []
        for c in ObjectConnection.objects.filter(
            __raw__={"connection": {"$elemMatch": {"object": self.id, "name": name}}}
        ):
            for x in c.connection:
                if x.object.id != self.id:
                    r += [[c, x.object, x.name]]
        return r

    def get_container(self) -> Optional["Object"]:
        """
        Get container for object.
        """
        c = self.parent
        while c:
            if not c.parent_connection:
                return c
            c = c.parent
        return None

    def get_box(self) -> "Object":
        """
        Get chassis.
        """
        if not self.parent or not self.parent_connection:
            return self
        return self.parent.get_box()

    def disconnect_p2p(self, name: str):
        """
        Remove connection *name*
        """
        from .objectconnection import ObjectConnection

        def move_to_container(obj: Object) -> None:
            """
            Move object to the nearest container.
            """
            c = obj.get_container()
            obj.parent = c
            obj.parent_connection = None
            obj.log(f"Insert into {c}", system="CORE", op="INSERT")
            obj.save()

        mc = self.model.get_model_connection(name)
        if not mc:
            return
        if mc.is_outer:
            move_to_container(self)
        elif mc.is_inner:
            o = Object.objects.filter(parent=self, parent_connection=name).first()
            if not o:
                return None
            move_to_container(o)
        elif mc.is_same_level:
            c, o, _ = self.get_p2p_connection(name)
            if not c:
                return
            self.log(f"'{name}' disconnected", system="CORE", op="DISCONNECT")
            c.delete()
            if o.is_wire and not ObjectConnection.objects.filter(connection__object=o.id).first():
                # Check wire connection and remove
                o.delete()

    def connect_p2p(
        self,
        name: str,
        remote_object: "Object",
        remote_name: str,
        data: Optional[Dict[str, Any]] = None,
        reconnect: bool = False,
    ) -> None:
        """
        Connect two genderless connections
        """
        from .objectconnection import ObjectConnection, ObjectConnectionItem

        lc = self.model.get_model_connection(name)
        if lc is None:
            raise ConnectionError("Local connection not found: %s" % name)
        name = lc.name
        rc = remote_object.model.get_model_connection(remote_name)
        if rc is None:
            raise ConnectionError("Remote connection not found: %s" % remote_name)
        remote_name = rc.name
        valid, cause = self.model.check_connection(lc, rc)
        if not valid:
            raise ConnectionError(cause)
        # Vertical connections
        if lc.is_outer:
            self.parent = remote_object
            self.parent_connection = remote_name
            self.save()
        elif lc.is_inner:
            remote_object.parent = self
            remote_object.parent_connection = name
            remote_object.save()
        elif lc.is_same_level:
            data = data or {}
            # Check existing connections
            if lc.type.genders in ("s", "m", "f", "mf"):
                ec, r_object, r_name = self.get_p2p_connection(name)
                if ec is not None:
                    # Connection exists
                    if reconnect:
                        if r_object.id == remote_object.id and r_name == remote_name:
                            # Same connection exists
                            n_data = deep_merge(ec.data, data)  # Merge ObjectConnection
                            if n_data != ec.data:
                                # Update data
                                ec.data = n_data
                                ec.save()
                            return
                        self.disconnect_p2p(name)
                    else:
                        raise ConnectionError("Already connected")
            # Create connection
            ObjectConnection(
                connection=[
                    ObjectConnectionItem(object=self, name=name),
                    ObjectConnectionItem(object=remote_object, name=remote_name),
                ],
                data=data,
            ).save()
        self.log(
            "%s:%s -> %s:%s" % (self, name, remote_object, remote_name), system="CORE", op="CONNECT"
        )

    def connect_genderless(
        self,
        name: str,
        remote_object: "Object",
        remote_name: str,
        data: Dict[str, Any] = None,
        type: Optional[str] = None,
        layer: Optional[Layer] = None,
    ):
        """
        Connect two genderless connections
        """
        from .objectconnection import ObjectConnection, ObjectConnectionItem

        lc = self.model.get_model_connection(name)
        if lc is None:
            raise ConnectionError("Local connection not found: %s" % name)
        name = lc.name
        rc = remote_object.model.get_model_connection(remote_name)
        if rc is None:
            raise ConnectionError("Remote connection not found: %s" % remote_name)
        remote_name = rc.name
        if lc.gender != "s":
            raise ConnectionError("Local connection '%s' must be genderless" % name)
        if rc.gender != "s":
            raise ConnectionError("Remote connection '%s' must be genderless" % remote_name)
        # Check for connection
        for c, ro, rname in self.get_genderless_connections(name):
            if ro.id == remote_object.id and rname == remote_name:
                c.data = data or {}
                c.save()
                return
        # Normalize layer
        if layer and isinstance(layer, str):
            layer = Layer.get_by_code(layer)
        # Create connection
        ObjectConnection(
            connection=[
                ObjectConnectionItem(object=self, name=name),
                ObjectConnectionItem(object=remote_object, name=remote_name),
            ],
            data=data or {},
            type=type or None,
            layer=layer,
        ).save()
        self.log(
            "%s:%s -> %s:%s" % (self, name, remote_object, remote_name), system="CORE", op="CONNECT"
        )

    def put_into(self, container: "Object") -> None:
        """
        Put object into container
        """
        if container and not container.is_container:
            raise ValueError("Must be put into container")
        # Connect to parent
        self.parent = container.id if container else None
        self.parent_connection = None
        # Reset previous rack position
        self.reset_data("rackmount", ("position", "side", "shift"))
        self.save()
        self.log("Insert into %s" % (container or "Root"), system="CORE", op="INSERT")

    def iter_used_connections(self) -> Iterable[str]:
        """
        Iterates used connections.
        """
        seen: Set[str] = set()
        for doc in Object._get_collection().find(
            {"parent": self.id}, {"_id": 0, "parent_connection": 1, "additional_connections": 1}
        ):
            parent_connection = doc.get("parent_connection")
            if parent_connection and parent_connection not in seen:
                yield parent_connection
                seen.add(parent_connection)
            additional_connections = doc.get("additional_connections")
            if additional_connections:
                for c in additional_connections:
                    if c not in seen:
                        yield c
                        seen.add(c)

    def attach(self, parent: "Object", parent_connection: str) -> None:
        """
        Attach object to parent slot.

        Args:
            parent: Parent object.
            parent_connection: Connection name.

        Raises:
            ConnectionError: When unable to connect.
        """
        # Check object is a module
        outer = self.model.get_outer()
        if not outer:
            raise ConnectionError("Object is not a module")
        # Check connection is exists
        cn = parent.model.get_model_connection(parent_connection)
        if not cn:
            msg = f"Parent connection is not found: {parent_connection}"
            raise ConnectionError(msg)
        # Check compatibility
        is_compatible, msg = parent.model.check_connection(cn, outer)
        if not is_compatible:
            msg = f"Not compatible: {msg}"
            raise ConnectionError(msg)
        # Process oversized objects
        size = self.occupied_slots
        additional = []
        if size > 1:
            additional = [
                cn.name
                for cn in parent.model.iter_next_connections(parent_connection, size - 1)
                if parent.model.check_connection(cn, outer)
            ]
            if len(additional) != size - 1:
                raise ConnectionError("Cannot be placed here")
        # Check if all slots is free
        used = set(parent.iter_used_connections())
        if used:
            if parent_connection is used:
                msg = f"Connection is used:{parent_connection}"
                raise ConnectionError(msg)
            if additional:
                s = used.intersection(set(additional))
                if s:
                    msg = f"Connection is used: {', '.join(s)}"
                    raise ConnectionError(msg)
        self.parent = parent
        self.parent_connection = parent_connection
        self.additional_connections = additional
        self.save()

    def iter_children(self) -> Iterable["Object"]:
        """
        Iterate through all children
        """
        yield from Object.objects.filter(parent=self.id)

    def get_local_name_path(self, include_chassis: bool = False) -> str:
        if self.parent and self.parent_connection:
            return self.parent.get_local_name_path(include_chassis) + [self.parent_connection]
        if include_chassis:
            return [self.name]
        return []

    def get_name_path(self) -> List[str]:
        """
        Return list of container names
        """
        if self.parent and self.parent_connection:
            return self.parent.get_name_path() + [self.parent_connection]
        elif self.parent:
            return self.parent.get_name_path() + [self.name]
        else:
            return [self.name]

    def log(self, message, user=None, system=None, managed_object=None, op=None):
        if not user:
            user = get_user()
        if hasattr(user, "username"):
            user = user.username
        if not user:
            user = "NOC"
        if not isinstance(managed_object, str):
            managed_object = smart_text(managed_object)
        ObjectLog(
            object=self.id,
            user=user,
            ts=datetime.datetime.now(),
            message=message,
            system=system,
            managed_object=managed_object,
            op=op,
        ).save()

    def get_log(self):
        return ObjectLog.objects.filter(object=self.id).order_by("ts")

    def get_lost_and_found(self) -> Optional["Object"]:
        m = ObjectModel.get_by_name("Lost&Found")
        c = self.parent
        while c:
            # Check siblings
            lf = Object.objects.filter(parent=c, model=m).first()
            if lf:
                return lf
            # Up one level
            c = c.parent
        return None

    @classmethod
    def detach_children(cls, sender, document, target=None):
        if not document.is_container:
            return
        if not target:
            target = document.get_lost_and_found()
        for o in Object.objects.filter(parent=document.id):
            if o.is_container:
                cls.detach_children(sender, o, target)
                o.delete()
            else:
                o.put_into(target)

    def iter_connections(self) -> Iterable[Tuple[str, "Object", str]]:
        """
        Iterate horizontal connections.

        Returns:
            Iterator of (name, remote object, remote name)

        Yields connections of specified direction as tuples of
        (name, remote_object, remote_name)
        """
        from .objectconnection import ObjectConnection

        for c in ObjectConnection.objects.filter(connection__object=self.id):
            local_name = None
            remote_side = None
            for cc in c.connection:
                if cc.object.id == self.id:
                    local_name = cc.name
                else:
                    remote_side = cc
            if local_name and remote_side:
                yield local_name, remote_side.object, remote_side.name

    @classmethod
    def delete_disconnect(cls, sender, document, target=None):
        from .objectconnection import ObjectConnection

        for c in ObjectConnection.objects.filter(connection__object=document.id):
            left = [cc for cc in c.connection if cc.object.id != document.id]
            if len(left) < 2:
                c.delete()  # Remove connection
            else:
                # Wipe object
                c.connection = left
                c.save()

    @property
    def is_pop(self) -> bool:
        """
        Check if object is point of presence
        """
        return bool(self.get_data("pop", "level"))

    def get_pop(self) -> Optional["Object"]:
        """
        Find enclosing PoP
        :returns: PoP instance or None
        """
        c = self.parent
        while c:
            if c.is_pop:
                return c
            c = c.parent
        return None

    def get_coordinates_zoom(self) -> Tuple[Optional[float], Optional[float], Optional[int]]:
        """
        Get managed object's coordinates
        # @todo: Speedup?
        :returns: x (lon), y (lat), zoom level
        """
        c = self
        while c:
            if c.point and c.layer:
                x, y = c.get_data_tuple("geopoint", ("x", "y"))
                zoom = c.layer.default_zoom or DEFAULT_ZOOM
                return x, y, zoom
            if c.parent:
                c = Object.get_by_id(c.parent.id)
                if c:
                    continue
            break
        return None, None, None

    @classmethod
    def get_managed(cls, mo) -> List["Object"]:
        """
        Get Object managed by managed object
        :param mo: Managed Object instance or id
        :returns: Objects managed by managed object, or empty list
        """
        if hasattr(mo, "id"):
            mo = mo.id
        return cls.objects.filter(
            data__match={"interface": "management", "attr": "managed_object", "value": mo}
        ).read_preference(ReadPreference.SECONDARY_PREFERRED)

    @classmethod
    def get_cpe(cls, cpe) -> Optional["Object"]:
        """
        Get Object CPE by cpe
        """
        if hasattr(cpe, "id"):
            cpe = str(cpe.id)
        return cls.objects.filter(
            data__match={"interface": "cpe", "attr": "cpe_id", "value": cpe}
        ).read_preference(ReadPreference.SECONDARY_PREFERRED)

    def iter_managed_object_id(self) -> Iterator[int]:
        for d in Object._get_collection().aggregate(
            [
                {"$match": {"_id": self.id}},
                # Get all nested objects and put them into the _path field
                {
                    "$graphLookup": {
                        "from": "noc.objects",
                        "connectFromField": "_id",
                        "connectToField": "parent",
                        "startWith": "$_id",
                        "as": "_path",
                        "maxDepth": 50,
                    }
                },
                # Leave only _path field
                {"$project": {"_id": 0, "_path": 1}},
                # Unwind _path array to separate documents
                {"$unwind": {"path": "$_path"}},
                # Move data one level up
                {"$project": {"data": "$_path.data"}},
                # Unwind data
                {"$unwind": {"path": "$data"}},
                # Convert nested data to flat document
                {
                    "$project": {
                        "interface": "$data.interface",
                        "attr": "$data.attr",
                        "value": "$data.value",
                    }
                },
                # Leave only management objects
                {"$match": {"interface": "management", "attr": "managed_object"}},
                # Leave only value
                {"$project": {"value": 1}},
            ]
        ):
            mo = d.get("value")
            if mo:
                yield mo

    @classmethod
    def get_by_path(cls, path: List[str], hints=None) -> Optional["Object"]:
        """
        Get object by given path.
        :param path: List of names following to path
        :param hints: {name: object_id} dictionary for getting object in path
        :returns: Object instance. None if not found
        """
        current = None
        for p in path:
            current = Object.objects.filter(name=p, parent=current).first()
            if not current:
                return None
            if hints:
                h = hints.get(p)
                if h:
                    return Object.get_by_id(h)
        return current

    def update_pop_links(self, delay: int = 20):
        call_later("noc.inv.util.pop_links.update_pop_links", delay, pop_id=self.id)

    def get_address_text(self) -> Optional[str]:
        """
        Return first found address.text value upwards the path
        :return: Address text or None
        """
        current = self
        while current:
            addr = current.get_data("address", "text")
            if addr:
                return addr
            if current.parent:
                current = Object.get_by_id(current.parent.id)
            else:
                break
        return None

    def get_object_serials(self, chassis_only: bool = True) -> List[str]:
        """
        Getting object serialNumber
        :param chassis_only: With serial numbers inner objects
        :return:
        """
        serials = [self.get_data("asset", "serial")]
        if not chassis_only:
            for oo in self.iter_children():
                serials += oo.get_object_serials(chassis_only=False)
        return serials

    def iter_technology(self, technologies: List["Technology"]) -> Iterable[PortItem]:
        """
        Iter object ports for technologies
        :param technologies: List for connection technologies
        :return:
        """

        def is_protocol_match(protocols) -> bool:
            for p in protocols:
                if p.protocol.technology in technologies:
                    return True
            return False

        connections = {
            ro.parent_connection: ro for ro in self.iter_children() if ro.model.cr_context != "XCVR"
        }
        for c in self.model.connections:
            if is_protocol_match(c.protocols):
                yield PortItem(
                    name=c.name,
                    protocols=[str(p) for p in c.protocols],
                    internal_name=c.internal_name,
                    path=[PathItem.from_object(self, c)],
                    combo=c.combo,
                )
            elif c.name in connections:
                ro = connections[c.name]
                for part_path in ro.iter_technology(technologies):
                    part_path.path = [PathItem.from_object(self, c)] + part_path.path
                    yield part_path

    def set_connection_interface(self, name, if_name):
        for cdata in self.connections:
            if cdata.name == name:
                cdata.interface_name = if_name
                return
        # New item
        self.connections += [ObjectConnectionData(name=name, interface_name=if_name)]

    def reset_connection_interface(self, name):
        self.connections = [c for c in self.connections if c.name != name]

    def _sync_sensors(self):
        """
        Synchronize sensors
        :return:
        """
        from .sensor import Sensor

        Sensor.sync_object(self)

    @classmethod
    def iter_by_address_id(
        cls, address: Union[str, List[str]], scope: str = None
    ) -> Iterable["Object"]:
        """
        Get objects
        :param address:
        :param scope:
        :return:
        """
        q = {
            "interface": "address",
            "scope": scope or "",
            "attr": "id",
        }
        if isinstance(address, list):
            if len(address) == 1:
                q["value"] = address[0]
            else:
                q["value__in"] = address
        else:
            q["value"] = address
        yield from cls.objects.filter(data__match=q)

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_object")

    @classmethod
    def get_agent(cls, agent):
        """
        Get Object managed by managed object
        :param agent: Agent instance or id
        :returns: Objects managed by managed object, or empty list
        """
        if hasattr(agent, "id"):
            agent = str(agent.id)
        return cls.objects.filter(
            data__match={"interface": "management", "attr": "managed_object", "value": agent}
        )

    def get_effective_agent(self) -> Optional[Agent]:
        """
        Find effective agent for object
        :return:
        """
        from noc.core.inv.path import find_path

        agent = self.get_data("agent", "agent")
        modbus = self.get_data("modbus", "type")
        if modbus and modbus in {"RTU", "ASCII"}:
            for name, _, _ in self.iter_connections():
                path = find_path(self, name, target_protocols=["<RS485-A", "<RS485-B"])
                if not path:
                    continue
                *_, lp = path
                agent = lp.obj.get_data("agent", "agent")
                if agent:
                    break
        if agent:
            agent = Agent.get_by_id(agent)
        return agent

    def get_topology_node(self) -> "TopologyNode":
        return TopologyNode(
            id=str(self.id),
            type="container",
            resource_id=str(self.id),
            title=self.name,
            title_metric_template="",
            stencil="Juniper/cloud",
            overlays=[],
            level=10,
            attrs={},
        )

    def iter_effective_crossing(self) -> Iterable[Crossing]:
        """
        Iterate objects all effective crossings.
        """
        if self.cross:
            yield from self.cross
        if self.model.cross:
            yield from self.model.cross

    def iter_cross(
        self, name: str, discriminators: Optional[Iterable[str]] = None
    ) -> Iterable[Crossing]:
        """
        Iterate crossed outputs.

        Given the input name and the optional discriminators,
        find and iterate all reachable outputs names.
        Process using dynamic crossings from objects and
        static crossings from models.
        """

        def is_passable(item: Crossing) -> bool:
            if not item.input_discriminator:
                return True
            if not discriminators:
                return False
            item_desc = discriminator(item.input_discriminator)
            return any(d in item_desc for d in discriminators)

        seen: Set[str] = set()
        discriminators = [discriminator(x) for x in discriminators or []]
        # Dynamic crossings
        for item in self.iter_effective_crossing():
            if item.input == name and item.output not in seen and is_passable(item):
                yield item
                seen.add(item.output)

    def set_internal_connection(self, input: str, output: str, data: Dict[str, str] = None):
        """ """
        input = self.model.get_model_connection(input)
        if not input:
            raise ValueError("Not found connection: %s" % input)
        output = self.model.get_model_connection(output)
        for c in self.cross:
            if c.input != input.name:
                continue
            # Update
            c.update_params(**data)
            break
        else:
            self.cross += [
                Crossing(
                    **{
                        "input": input.name,
                        "input_discriminator": data.get("input_discriminator"),
                        "output": output.name,
                        "output_discriminator": data.get("output_discriminator"),
                        "gain_db": data.get("gain_db"),
                    }
                )
            ]

    def disconnect_internal(self, name: str, remote_name: Optional[str] = None):
        """
        Remove internal crossing
        """
        if not self.model.has_connection(name):
            raise ValueError("Unknown input")
        self.cross = [
            c
            for c in self.cross
            if c.input != name and (not remote_name or remote_name == c.output)
        ]

    def as_resource(self, path: Optional[str] = None) -> str:
        """
        Convert instance or connection to the resource reference.

        Args:
            path: Optional connection name

        Returns:
            Resource reference
        """
        if path:
            return f"o:{self.id}:{path}"
        return f"o:{self.id}"

    def refresh_pop_links(self) -> None:
        """
        Update PoP links if necessary
        """
        pop = self.get_pop()
        if pop:
            pop.update_pop_links()

    def _get_container(self) -> Optional["Object"]:
        """
        Emulates deprecated container property
        """
        warnings.warn(
            "Object.container is deprecated and will be removed in NOC 25.1",
            RemovedInNOC2501Warning,
        )
        if self.parent_connection:
            return None
        return self.parent

    def _set_container(self, value: Optional["Object"]) -> None:
        warnings.warn(
            "Object.container is deprecated and will be removed in NOC 25.1",
            RemovedInNOC2501Warning,
        )
        self.parent_connection = None
        self.parent = value

    container = property(fget=_get_container, fset=_set_container, doc="Legacy container attribute")

    @property
    def occupied_slots(self) -> int:
        """
        Returns amount of occupied slots.

        Returns:
            0: For cards without outer connections.
            1: For standard-sized cards.
            2+: For oversized cards.
        """
        # Check we have outer connection
        if not self.model.get_outer():
            return 0
        # Chec if we have oversized card
        size = self.model.get_data("caps", "multi_slot")
        if size:
            return size
        # Standard size
        return 1


signals.pre_delete.connect(Object.detach_children, sender=Object)
signals.pre_delete.connect(Object.delete_disconnect, sender=Object)
