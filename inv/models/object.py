# ---------------------------------------------------------------------
# ObjectModel model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import operator
from dataclasses import dataclass
from threading import Lock
from typing import Optional, Any, Dict, Union, List, Set, Iterator

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


@Label.model
@bi_sync
@on_save
@change
@on_delete_check(
    check=[
        ("sa.ManagedObject", "container"),
        ("inv.CoveredObject", "object"),
        ("inv.Object", "container"),
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
            "container",
            ("name", "container"),
            ("data.interface", "data.attr", "data.value"),
            "labels",
            "effective_labels",
        ],
    }

    name = StringField()
    model: "ObjectModel" = PlainReferenceField(ObjectModel)
    data: List["ObjectAttr"] = ListField(EmbeddedDocumentField(ObjectAttr))
    container: Optional["Object"] = PlainReferenceField("self", required=False)
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

    def iter_changed_datastream(self, changed_fields=None):
        if config.datastream.enable_managedobject:
            if self.data and self.get_data("management", "managed_object"):
                yield "managedobject", self.get_data("management", "managed_object")
            else:
                for _, o, _ in self.iter_outer_connections():
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
            for co in Object.objects.filter(container=o.id):
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
            if self.container:
                pop = self.get_pop()
                if pop:
                    pop.update_pop_links()
        # Changed container
        elif hasattr(self, "_changed_fields") and "container" in self._changed_fields:
            # Old pop
            old_container_id = getattr(self, "_old_container", None)
            old_pop = None
            if old_container_id:
                c = Object.get_by_id(old_container_id)
                while c:
                    if c.get_data("pop", "level"):
                        old_pop = c
                        break
                    c = c.container
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
        if self.container:
            return self.container.get_path() + [self.id]
        return [self.id]

    @property
    def level(self) -> int:
        """
        Return level
        :return:
        """
        if not self.container:
            return 0
        return len(self.get_path()) - 1  # self

    @property
    def has_children(self) -> bool:
        return bool(Object.objects.filter(container=self.id))

    @property
    def is_wire(self) -> bool:
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

    def get_nested_ids(self):
        """
        Return id of this and all nested object
        :return:
        """
        # $graphLookup hits 100Mb memory limit. Do not use it
        seen = {self.id}
        wave = {self.id}
        max_level = 4
        coll = Object._get_collection()
        for _ in range(max_level):
            # Get next wave
            wave = (
                set(d["_id"] for d in coll.find({"container": {"$in": list(wave)}}, {"_id": 1}))
                - seen
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

    # def iter_model_configuration_params(self) -> Tuple["ConfigurationParam", "ParamSchema", "ScopeVariant"]:
    #     """
    #     Iterate over Available Configuration Param
    #     """
    #     # Processed configurations param
    #     for pr in self.model.configuration_rule.param_rules:

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

    def get_connection_proposals(
        self,
        name,
        ro: "ObjectModel",
        remote_name: Optional[str] = None,
        use_cable: bool = False,
        only_first: bool = False,
    ) -> List[Tuple[Optional["ObjectModel"], str]]:
        """

        :param name:
        :param ro:
        :param remote_name:
        :param use_cable:
        :param only_first:
        :return:
        """
        r = []
        for model_id, c_name in self.model.get_connection_proposals(name):
            if use_cable:
                model = ObjectModel.get_by_id(model_id)
                if bool(model.get_data("length", "length")):
                    # Wired, Multiple Cable?
                    r.append((model, c_name))
            elif remote_name and c_name != remote_name:
                continue
            elif ro and ro.id == model_id:
                r.append((None, c_name))
            if only_first and r:
                return r
            # Check connection
        return r

    def has_connection(self, name):
        return self.model.has_connection(name)

    def get_p2p_connection(
        self, name: str
    ) -> Tuple[Optional[Any], Optional["Object"], Optional[str]]:
        """
        Get neighbor for p2p connection (s and mf types)
        Returns connection, remote object, remote connection or
        None, None, None
        """
        from .objectconnection import ObjectConnection

        c = ObjectConnection.objects.filter(
            __raw__={"connection": {"$elemMatch": {"object": self.id, "name": name}}}
        ).first()
        if c:
            for x in c.connection:
                if x.object.id != self.id:
                    return c, x.object, x.name
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
        # Direct container
        if self.container:
            return self.container
        # Outer
        for _, c, _ in self.iter_outer_connections():
            return c.get_container()
        return None

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
            obj.container = c
            obj.log(f"Insert into {c}", system="CORE", op="INSERT")
            obj.save()

        c, o, _ = self.get_p2p_connection(name)
        if not c:
            return
        mc = self.model.get_model_connection(name)
        if mc:
            if mc.is_outer:
                move_to_container(self)
            elif mc.is_inner:
                move_to_container(o)
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
        data: Dict[str, Any],
        reconnect: bool = False,
    ) -> Optional[Any]:
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
        c = ObjectConnection(
            connection=[
                ObjectConnectionItem(object=self, name=name),
                ObjectConnectionItem(object=remote_object, name=remote_name),
            ],
            data=data,
        ).save()
        self.log(
            "%s:%s -> %s:%s" % (self, name, remote_object, remote_name), system="CORE", op="CONNECT"
        )
        # Disconnect from container on o-connection
        for obj, conn in [(self, lc), (remote_object, rc)]:
            if obj.container and conn.is_outer:
                obj.log("Remove from %s" % obj.container, system="CORE", op="REMOVE")
                obj.container = None
                obj.save()
        return c

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

    def put_into(self, container: "Object"):
        """
        Put object into container
        """
        if container and not container.get_data("container", "container"):
            raise ValueError("Must be put into container")
        # Disconnect all o-connections
        for c in self.model.connections:
            if c.direction == "o":
                c, _, _ = self.get_p2p_connection(c.name)
                if c:
                    self.disconnect_p2p(c.name)
        # Connect to parent
        self.container = container.id if container else None
        # Reset previous rack position
        self.reset_data("rackmount", ("position", "side", "shift"))
        #
        self.save()
        self.log("Insert into %s" % (container or "Root"), system="CORE", op="INSERT")

    def get_content(self) -> "Object":
        """
        Returns all items directly put into container
        """
        return Object.objects.filter(container=self.id)

    def get_local_name_path(self, include_chassis: bool = False) -> str:
        for _, ro, rn in self.get_outer_connections():
            return ro.get_local_name_path(include_chassis) + [rn]
        if include_chassis:
            return [self.name]
        return []

    def get_name_path(self) -> List[str]:
        """
        Return list of container names
        """
        current = self.container
        if current is None:
            for _, ro, rn in self.get_outer_connections():
                return ro.get_name_path() + [rn]
            return [smart_text(self)]
        np = [smart_text(self)]
        while current:
            np.insert(0, smart_text(current))
            current = current.container
        return np

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
        c = self.container
        while c:
            # Check siblings
            lf = Object.objects.filter(container=c, model=m).first()
            if lf:
                return lf
            # Up one level
            c = c.container
        return None

    @classmethod
    def detach_children(cls, sender, document, target=None):
        if not document.get_data("container", "container"):
            return
        if not target:
            target = document.get_lost_and_found()
        for o in Object.objects.filter(container=document.id):
            if o.get_data("container", "container"):
                cls.detach_children(sender, o, target)
                o.delete()
            else:
                o.put_into(target)

    def iter_connections(self, direction: Optional[str]) -> Iterable[Tuple[str, "Object", str]]:
        """
        Yields connections of specified direction as tuples of
        (name, remote_object, remote_name)
        """
        from .objectconnection import ObjectConnection

        ic = set(c.name for c in self.model.connections if c.direction == direction)
        for c in ObjectConnection.objects.filter(connection__object=self.id):
            sn = None
            oc = None
            for cc in c.connection:
                if cc.object.id == self.id:
                    if cc.name in ic:
                        sn = cc.name
                else:
                    oc = cc
            if sn and oc:
                yield sn, oc.object, oc.name

    def iter_inner_connections(self):
        """
        Yields inner connections as tuples of
        (name, remote_object, remote_name)
        """
        yield from self.iter_connections("i")

    def iter_outer_connections(self):
        """
        Yields outer connections as tuples of
        (name, remote_object, remote_name)
        """
        yield from self.iter_connections("o")

    def has_inner_connections(self):
        """
        Returns True if object has any inner connections
        """
        return any(self.iter_inner_connections())

    def get_inner_connections(self):
        """
        Returns a list of inner connections as
        (name, remote_object, remote_name)
        """
        return list(self.iter_inner_connections())

    def get_outer_connections(self):
        """
        Returns a list of outer connections as
        (name, remote_object, remote_name)
        """
        return list(self.iter_outer_connections())

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

    def get_pop(self) -> Optional["Object"]:
        """
        Find enclosing PoP
        :returns: PoP instance or None
        """
        c = self.container
        while c:
            if c.get_data("pop", "level"):
                return c
            c = c.container
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
            if c.container:
                c = Object.get_by_id(c.container.id)
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
                        "connectToField": "container",
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
            current = Object.objects.filter(name=p, container=current).first()
            if not current:
                return None
            if hints:
                h = hints.get(p)
                if h:
                    return Object.get_by_id(h)
        return current

    def update_pop_links(self, delay: int = 20):
        call_later("noc.inv.util.pop_links.update_pop_links", delay, pop_id=self.id)

    @classmethod
    def _pre_init(cls, sender, document, values, **kwargs):
        """
        Object pre-initialization
        """
        # Store original container id
        if "container" in values and values["container"]:
            document._cache_container = values["container"]

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
            if current.container:
                current = Object.get_by_id(current.container.id)
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
            for sn, oo, name in self.iter_inner_connections():
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
            name: ro
            for name, ro, _ in self.iter_inner_connections()
            if ro.model.cr_context != "XCVR"
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
            for name, remote_object, remote_name in self.iter_connections("s"):
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

    def iter_cross(
        self, name: str, discriminators: Optional[Iterable[str]] = None
    ) -> Iterable[str]:
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

        def iter_merge(
            i1: Optional[Iterable[Crossing]], i2: Optional[Iterable[Crossing]]
        ) -> Iterable[Crossing]:
            if i1:
                yield from i1
            if i2:
                yield from i2

        seen: Set[str] = set()
        discriminators = [discriminator(x) for x in discriminators or []]
        # Dynamic crossings
        # if self.cross:
        for item in iter_merge(self.cross, self.model.cross):
            # @todo: Restrict to type `s`?
            if item.input == name and item.output not in seen and is_passable(item):
                yield item.output
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


signals.pre_delete.connect(Object.detach_children, sender=Object)
signals.pre_delete.connect(Object.delete_disconnect, sender=Object)
signals.pre_init.connect(Object._pre_init, sender=Object)
