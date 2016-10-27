## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ObjectModel model
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import operator
from threading import RLock
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, DictField, ObjectIdField,
                                ListField, PointField, ReferenceField)
from mongoengine import signals
import cachetools
import six
## NOC modules
from connectiontype import ConnectionType
from objectmodel import ObjectModel
from modelinterface import ModelInterface
from objectlog import ObjectLog
from noc.gis.models.layer import Layer
from error import ConnectionError, ModelDataError
from noc.lib.nosql import PlainReferenceField
from noc.lib.utils import deep_merge
from noc.lib.middleware import get_user
from noc.core.gridvcs.manager import GridVCSField
from noc.core.defer import call_later
from noc.core.model.decorator import on_save

id_lock = RLock()


@on_save
class Object(Document):
    """
    Inventory object
    """
    meta = {
        "collection": "noc.objects",
        "allow_inheritance": False,
        "indexes": [
            "data",
            "container",
            ("name", "container"),
            ("model", "data.asset.serial"),
            "data.management.managed_object"
        ]
    }

    name = StringField()
    model = PlainReferenceField(ObjectModel)
    data = DictField()
    container = ObjectIdField(required=False)
    comment = GridVCSField("object_comment")
    # Map
    layer = ReferenceField(Layer)
    point = PointField(auto_index=True)
    #
    tags = ListField(StringField())

    _id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _path_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

    REBUILD_CONNECTIONS = [
        "links",
        "conduits"
    ]

    def __unicode__(self):
        return unicode(self.name or self.id)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return Object.objects.filter(id=id).first()

    def clean(self):
        self.set_point()

    def set_point(self):
        from noc.gis.map import map

        self.layer = None
        self.point = None
        geo = self.data.get("geopoint")
        if not geo:
            return
        layer_code = self.model.get_data("geopoint", "layer")
        if not layer_code:
            return
        layer = Layer.get_by_code(layer_code)
        if not layer:
            return
        x = geo.get("x")
        y = geo.get("y")
        srid = geo.get("srid")
        if x and y:
            self.layer = layer
            self.point = map.get_db_point(x, y, srid=srid)

    def on_save(self):
        geo = self.data.get("geopoint")
        if geo and geo.get("x") and geo.get("y"):
            # Rebuild connection layers
            for ct in self.REBUILD_CONNECTIONS:
                for c, _, _ in self.get_genderless_connections(ct):
                    c.save()  # set_line(

    @cachetools.cachedmethod(operator.attrgetter("_path_cache"), lock=lambda _: id_lock)
    def get_path(self):
        """
        Returns list of parent segment ids
        :return:
        """
        if self.container:
            c = Object.get_by_id(self.container)
            if c:
                return c.get_path() + [self.id]
        return [self.id]

    def get_data(self, interface, key):
        attr = ModelInterface.get_interface_attr(interface, key)
        if attr.is_const:
            # Lookup model
            return self.model.get_data(interface, key)
        else:
            v = self.data.get(interface, {})
            return v.get(key)

    def set_data(self, interface, key, value):
        attr = ModelInterface.get_interface_attr(interface, key)
        if attr.is_const:
            raise ModelDataError("Cannot set read-only value")
        value = attr._clean(value)
        # @todo: Check interface restrictions
        if interface not in self.data:
            self.data[interface] = {}
        self.data[interface][key] = value

    def reset_data(self, interface, key):
        attr = ModelInterface.get_interface_attr(interface, key)
        if attr.is_const:
            raise ModelDataError("Cannot reset read-only value")
        if interface in self.data and key in self.data[interface]:
            del self.data[interface][key]

    def has_connection(self, name):
        return self.model.has_connection(name)

    def get_p2p_connection(self, name):
        """
        Get neighbor for p2p connection (s and mf types)
        Returns connection, remote object, remote connection or
        None, None, None
        """
        c = ObjectConnection.objects.filter(
            __raw__={
                "connection": {
                    "$elemMatch": {
                        "object": self.id,
                        "name": name
                    }
                }
            }
        ).first()
        if c:
            for x in c.connection:
                if x.object.id != self.id:
                    return c, x.object, x.name
        # Strange things happen
        return None, None, None

    def get_genderless_connections(self, name):
        r = []
        for c in ObjectConnection.objects.filter(
            __raw__={
                "connection": {
                    "$elemMatch": {
                        "object": self.id,
                        "name": name
                    }
                }
            }
        ):
            for x in c.connection:
                if x.object.id != self.id:
                    r += [[c, x.object, x.name]]
        return r

    def disconnect_p2p(self, name):
        """
        Remove connection *name*
        """
        c = self.get_p2p_connection(name)[0]
        if c:
            self.log(u"'%s' disconnected" % name,
                     system="CORE", op="DISCONNECT")
            c.delete()

    def connect_p2p(self, name, remote_object, remote_name, data,
                    reconnect=False):
        lc = self.model.get_model_connection(name)
        if lc is None:
            raise ConnectionError("Local connection not found: %s" % name)
        name = lc.name
        rc = remote_object.model.get_model_connection(remote_name)
        if rc is None:
            raise ConnectionError("Remote connection not found: %s" % remote_name)
        remote_name = rc.name
        # Check genders are compatible
        r_gender = ConnectionType.OPPOSITE_GENDER[rc.gender]
        if lc.gender != r_gender:
            raise ConnectionError("Incompatible genders: %s - %s" % (
                lc.gender, rc.gender
            ))
        # Check directions are compatible
        if ((lc.direction == "i" and rc.direction != "o") or
                (lc.direction == "o" and rc.direction != "i") or
                (lc.direction == "s" and rc.direction != "s")):
            raise ConnectionError("Incompatible directions: %s - %s" % (
                lc.direction, rc.direction))
        # Check types are compatible
        c_types = lc.type.get_compatible_types(lc.gender)
        if rc.type.id not in c_types:
            raise ConnectionError("Incompatible connection types: %s - %s" % (
                lc.type.name, rc.type.name
            ))
        # Check existing connecitons
        if lc.type.genders in ("s", "m", "f", "mf"):
            ec, r_object, r_name = self.get_p2p_connection(name)
            if ec is not None:
                # Connection exists
                if reconnect:
                    if (r_object.id == remote_object.id and
                        r_name == remote_name):
                        # Same connection exists
                        n_data = deep_merge(ec.data, data)
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
                ObjectConnectionItem(object=remote_object,
                                     name=remote_name)
            ],
            data=data
        ).save()
        self.log(u"%s:%s -> %s:%s" % (self, name, remote_object, remote_name),
                 system="CORE", op="CONNECT")
        # Disconnect from container on o-connection
        if lc.direction == "o" and self.container:
            self.log(u"Remove from %s" % self.container,
                     system="CORE", op="REMOVE")
            self.container = None
            self.save()
        return c

    def connect_genderless(self, name, remote_object, remote_name,
                           data=None, type=None, layer=None):
        """
        Connect two genderless connections
        """
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
        if layer and isinstance(layer, six.string_types):
            layer = Layer.get_by_code(layer)
        # Create connection
        ObjectConnection(
            connection=[
                ObjectConnectionItem(object=self, name=name),
                ObjectConnectionItem(object=remote_object,
                                     name=remote_name)
            ],
            data=data or {},
            type=type or None,
            layer=layer
        ).save()
        self.log(u"%s:%s -> %s:%s" % (self, name, remote_object, remote_name),
                 system="CORE", op="CONNECT")

    def put_into(self, container):
        """
        Put object into container
        """
        if not container.get_data("container", "container"):
            raise ValueError("Must be put into container")
        # Disconnect all o-connections
        for c in self.model.connections:
            if c.direction == "o":
                c, _, _ = self.get_p2p_connection(c.name)
                if c:
                    self.disconnect_p2p(c.name)
        # Connect to parent
        self.container = container.id
        # Reset previous rack position
        if self.data.get("rackmount"):
            for k in ("position", "side", "shift"):
                if k in self.data["rackmount"]:
                    del self.data["rackmount"][k]
        self.save()
        self.log(
            "Insert into %s" % container,
            system="CORE", op="INSERT")

    def get_content(self):
        """
        Returns all items directly put into container
        """
        return Object.objects.filter(container=self.id)

    def get_local_name_path(self):
        for _, ro, rn in self.get_outer_connections():
            return ro.get_local_name_path() + [rn]
        return []

    def get_name_path(self):
        """
        Return list of container names
        """
        c = self.container
        if c is None:
            for _, ro, rn in self.get_outer_connections():
                return ro.get_name_path() + [rn]
            return [unicode(self)]
        np = [unicode(self)]
        while c:
            o = Object.objects.filter(id=c).first()
            if o:
                np = [unicode(o)] + np
                c = o.container
            else:
                break
        return np[1:]

    def log(self, message, user=None, system=None,
            managed_object=None, op=None):
        if not user:
            user = get_user()
        if hasattr(user, "username"):
            user = user.username
        if not user:
            user = "NOC"
        if not isinstance(managed_object, basestring):
            managed_object = unicode(managed_object)
        ObjectLog(
            object=self.id,
            user=user,
            ts=datetime.datetime.now(),
            message=message,
            system=system,
            managed_object=managed_object,
            op=op
        ).save()

    def get_log(self):
        return ObjectLog.objects.filter(object=self.id).order_by("ts")

    def get_lost_and_found(self):
        c = self.container
        while c:
            # Check siblings
            for x in Object.objects.filter(container=c):
                if x.model.name == "Lost&Found":
                    return x
            # Up level
            c = Object.objects.get(id=c)
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

    def iter_connections(self, direction):
        """
        Yields connections of specified direction as tuples of
        (name, remote_object, remote_name)
        """
        ic = set(c.name for c in self.model.connections if c.direction == direction)
        for c in ObjectConnection.objects.filter(
                connection__object=self.id):
            sn = None
            oc = None
            for cc in c.connection:
                if cc.object.id == self.id:
                    if cc.name in ic:
                        sn = cc.name
                else:
                    oc = cc
            if sn and oc:
                yield (sn, oc.object, oc.name)

    def iter_inner_connections(self):
        """
        Yields inner connections as tuples of
        (name, remote_object, remote_name)
        """
        for r in self.iter_connections("i"):
            yield r

    def iter_outer_connections(self):
        """
        Yields outer connections as tuples of
        (name, remote_object, remote_name)
        """
        for r in self.iter_connections("o"):
            yield r

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
        for c in ObjectConnection.objects.filter(
                connection__object=document.id):
            left = [cc for cc in c.connection
                    if cc.object.id != document.id]
            if len(left) < 2:
                c.delete()  # Remove connection
            else:
                # Wipe object
                c.connection = left
                c.save()

    def get_pop(self):
        """
        Find enclosing PoP
        :returns: PoP instance or None
        """
        c = self.container
        while c:
            o = Object.get_by_id(c)
            if not o:
                break
            if o.get_data("pop", "level"):
                return o
            c = o.container
        return None

    @classmethod
    def get_managed(cls, mo):
        """
        Get Object managed by managed object
        :param mo: Managed Object instance or id
        :returns: Objects managed by managed object, or empty list
        """
        if hasattr(mo, "id"):
            mo = mo.id
        return cls.objects.filter(data__management__managed_object=mo)

    @classmethod
    def get_root(cls):
        """
        Returns Root container
        """
        root = getattr(cls, "_root_container", None)
        if not root:
            rm = ObjectModel.objects.get(name="Root")
            root = Object.objects.get(model=rm.id)
            cls._root_container = root
        return root

    @classmethod
    def get_by_path(cls, path):
        """
        Get object by given path.
        :param path: List of names following to path
        :returns: Object instance. None if not found
        """
        current = cls.get_root()
        for p in path:
            if not current:
                break
            current = Object.objects.filter(
                name=p,
                container=current.id
            ).first()
        return current

    @classmethod
    def change_container(cls, sender, document, target=None,
                         created=False, **kwargs):
        if created:
            if document.container:
                pop = document.get_pop()
                if pop:
                    call_later(
                        "noc.inv.util.pop_links.update_pop_links",
                        20,
                        pop_id=pop.id
                    )
            return
        # Changed object
        if not hasattr(document, "_changed_fields") or "container" not in document._changed_fields:
            return
        old_container = getattr(document, "_cache_container", None)
        old_pop = None
        new_pop = None
        # Old pop
        if old_container:
            c = old_container
            while c:
                o = Object.objects.get(id=c)
                if o.get_data("pop", "level"):
                    old_pop = o.id
                    break
                c = o.container
        # New pop
        pop = document.get_pop()
        if pop:
            new_pop = pop.id
        if old_pop != new_pop:
            if old_pop:
                call_later(
                    "noc.inv.util.pop_links.update_pop_links",
                    20,
                    pop_id=old_pop
                )
            if new_pop:
                call_later(
                    "noc.inv.util.pop_links.update_pop_links",
                    20,
                    pop_id=new_pop
                )

    @classmethod
    def _pre_init(cls, sender, document, values, **kwargs):
        """
        Object pre-initialization
        """
        if "container" in values and values["container"]:
            document._cache_container = values["container"]

signals.pre_delete.connect(Object.detach_children, sender=Object)
signals.pre_delete.connect(Object.delete_disconnect, sender=Object)
signals.post_save.connect(Object.change_container, sender=Object)
signals.pre_init.connect(Object._pre_init, sender=Object)

## Avoid circular references
from objectconnection import ObjectConnection, ObjectConnectionItem
