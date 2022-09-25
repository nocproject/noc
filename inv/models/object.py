# ---------------------------------------------------------------------
# ObjectModel model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import operator
from threading import Lock
from collections import namedtuple
from typing import Optional, Any, Dict, Union, List, Set, Iterator

# Third-party modules
from pymongo import ReadPreference
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    ListField,
    PointField,
    LongField,
    EmbeddedDocumentField,
    DynamicField,
    ReferenceField,
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
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.label import Label
from noc.core.comp import smart_text
from noc.config import config
from noc.pm.models.agent import Agent
from .objectmodel import ObjectModel
from .modelinterface import ModelInterface
from .objectlog import ObjectLog
from .error import ConnectionError, ModelDataError

PathItem = namedtuple("PathItem", ["object", "connection"])

id_lock = Lock()
_path_cache = cachetools.TTLCache(maxsize=1000, ttl=60)


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
    model = PlainReferenceField(ObjectModel)
    data = ListField(EmbeddedDocumentField(ObjectAttr))
    container = PlainReferenceField("self", required=False)
    comment = GridVCSField("object_comment")
    # Map
    layer = PlainReferenceField(Layer)
    point = PointField(auto_index=True)
    # Additional connection data
    connections = ListField(EmbeddedDocumentField(ObjectConnectionData))
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
    def get_by_id(cls, id) -> Optional["Object"]:
        return Object.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id) -> Optional["Object"]:
        return Object.objects.filter(bi_id=id).first()

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

    def get_data(self, interface: str, key: str, scope: Optional[str] = None) -> Any:
        attr = ModelInterface.get_interface_attr(interface, key)
        if attr.is_const:
            # Lookup model
            return self.model.get_data(interface, key)
        for item in self.data:
            if item.interface == interface and item.attr == key:
                if not scope or item.scope == scope:
                    return item.value
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
        for i in self.model.data:
            for a in self.model.data[i]:
                k = (i, a, "")
                if k in seen:
                    continue
                r += [ObjectAttr(interface=i, attr=a, scope="", value=self.model.data[i][a])]
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

    def disconnect_p2p(self, name: str):
        """
        Remove connection *name*
        """
        c = self.get_p2p_connection(name)[0]
        if c:
            self.log("'%s' disconnected" % name, system="CORE", op="DISCONNECT")
            c.delete()

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
        # Check existing connecitons
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
        if lc.direction == "o" and self.container:
            self.log("Remove from %s" % self.container, system="CORE", op="REMOVE")
            self.container = None
            self.save()
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

    def get_local_name_path(self):
        for _, ro, rn in self.get_outer_connections():
            return ro.get_local_name_path() + [rn]
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
    def get_managed(cls, mo) -> Optional["Object"]:
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
        Gettint object serialNumber
        :param chassis_only: With serial numbers inner objects
        :return:
        """
        serials = [self.get_data("asset", "serial")]
        if not chassis_only:
            for sn, oo, name in self.iter_inner_connections():
                serials += oo.get_object_serials(chassis_only=False)
        return serials

    def iter_scope(self, scope: str) -> Iterable[Tuple[PathItem, ...]]:
        """
        Yields Full physical path for all connections with given scopes
        behind the object

        :param scope: Scope name
        :return:
        """
        connections = {name: ro for name, ro, _ in self.iter_inner_connections()}
        for c in self.model.connections:
            if c.type.is_matched_scope(scope, c.protocols):
                # Yield connection
                yield PathItem(object=self, connection=c),
            elif c.name in connections:
                ro = connections[c.name]
                for part_path in ro.iter_scope(scope):
                    yield (PathItem(object=self, connection=c),) + part_path

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
                print(name, remote_object, remote_name)
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


signals.pre_delete.connect(Object.detach_children, sender=Object)
signals.pre_delete.connect(Object.delete_disconnect, sender=Object)
signals.pre_init.connect(Object._pre_init, sender=Object)
