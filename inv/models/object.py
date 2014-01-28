## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ObjectModel model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, DictField, ObjectIdField
from mongoengine import signals
## NOC modules
from connectiontype import ConnectionType
from objectmodel import ObjectModel
from modelinterface import ModelInterface
from objectlog import ObjectLog
from error import ConnectionError, ModelDataError
from noc.lib.nosql import PlainReferenceField
from noc.lib.utils import deep_merge
from noc.lib.middleware import get_user
from noc.lib.gridvcs.manager import GridVCSField
from noc.gis.map import map


class Object(Document):
    """
    Inventory object
    """
    meta = {
        "collection": "noc.objects",
        "allow_inheritance": False,
        "indexes": ["data", "container"]
    }

    name = StringField()
    model = PlainReferenceField(ObjectModel)
    data = DictField()
    container = ObjectIdField(required=False)
    comment = GridVCSField("object_comment")

    def __unicode__(self):
        return unicode(self.name or self.id)

    def get_interface_attr(self, interface, key):
        mi = ModelInterface.objects.filter(name=interface).first()
        if not mi:
            raise ModelDataError("Invalid interface '%s'" % interface)
        attr = mi.get_attr(key)
        if not attr:
            raise ModelDataError("Invalid attribute '%s.%s'" % (
                interface, key))
        return attr

    def get_data(self, interface, key):
        attr = self.get_interface_attr(interface, key)
        if attr.is_const:
            # Lookup model
            return self.model.get_data(interface, key)
        else:
            v = self.data.get(interface, {})
            return v.get(key)

    def set_data(self, interface, key, value):
        attr = self.get_interface_attr(interface, key)
        if attr.is_const:
            raise ModelDataError("Cannot set read-only value")
        value = attr.clean(value)
        # @todo: Check interface restrictions
        if interface not in self.data:
            self.data[interface] = {}
        self.data[interface][key] = value

    def reset_data(self, interface, key):
        attr = self.get_interface_attr(interface, key)
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
            self.log("'%s' disconnected" % name,
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
        self.log("%s:%s -> %s:%s" % (self, name, remote_object, remote_name),
                 system="CORE", op="CONNECT")
        # Disconnect from container on o-connection
        if lc.direction == "o" and self.container:
            self.log("Remove from %s" % self.container,
                     system="CORE", op="REMOVE")
            self.container = None
            self.save()
        return c

    def connect_genderless(self, name, remote_object, remote_name,
                           data=None, type=None):
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
        # Create connection
        ObjectConnection(
            connection=[
                ObjectConnectionItem(object=self, name=name),
                ObjectConnectionItem(object=remote_object,
                                     name=remote_name)
            ],
            data=data or {},
            type=type or None
        ).save()
        self.log("%s:%s -> %s:%s" % (self, name, remote_object, remote_name),
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
        r = []
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
    def set_geo_point(cls, sender, document, target=None, **kwargs):
        """
        Update map point
        """
        # Check geopoint interface is supported
        layer = document.get_data("geopoint", "layer")
        if not layer:
            return
        x = document.get_data("geopoint", "x")
        y = document.get_data("geopoint", "y")
        srid = document.get_data("geopoint", "srid")
        if not x or not y:
            map.delete_point(document.id, layer)
        else:
            map.set_point(document.id, layer, x, y, srid=srid, label=document.name)

    @classmethod
    def delete_geo_point(cls, sender, document, target=None):
        # Check geopoint interface is supported
        layer = document.get_data("geopoint", "layer")
        if not layer:
            return
        map.delete_point(document.id)


signals.pre_delete.connect(Object.detach_children, sender=Object)
signals.pre_delete.connect(Object.delete_geo_point, sender=Object)
signals.post_save.connect(Object.set_geo_point, sender=Object)

## Avoid circular references
from objectconnection import ObjectConnection, ObjectConnectionItem
