## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ObjectModel model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, DictField
## NOC modules
from noc.inv.models.connectiontype import ConnectionType
from noc.inv.models.objectmodel import ObjectModel
from noc.lib.nosql import PlainReferenceField


class Object(Document):
    """
    Inventory object
    """
    meta = {
        "collection": "noc.objects",
        "allow_inheritance": False,
        "indexes": ["data"]
    }

    name = StringField()
    model = PlainReferenceField(ObjectModel)
    data = DictField()

    def __unicode__(self):
        return self.name

    def get_data(self, interface, key):
        v = self.data.get(interface, {})
        return v.get(key)

    def set_data(self, interface, key, value):
        if interface not in self.data:
            self.data[interface] = {}
        self.data[interface][key] = value

    def get_p2p_connection(self, name):
        """
        Get neighbor for p2 connection (s and mf types)
        Returns connection, remote object, remote connection or
        None, None, None
        """
        c = ObjectConnection.objects.filter(
            connection__object=self.id,
            connection__name=self.id).first()
        for x in c.connection:
            if x.object.id != self.id or x.name != name:
                return c, x.object, x.name
        # Strange things happen
        return None, None, None

    def disconnect_p2p(self, name):
        """
        Remove connection *name*
        """
        for c, _, _ in self.get_p2p_connection(name):
            c.delete()

    def connect_p2p(self, name, remote_object, remote_name, data):
        lc = self.model.get_model_connection(name)
        if lc is not None:
            raise ValueError("Local connection not found: %s" % name)
        rc = remote_object.model.get_model_connection(remote_name)
        if rc is not None:
            raise ValueError("Remote connection not found: %s" % remote_name)
        # Check genders are compatible
        r_gender = ConnectionType.OPPOSITE_GENDER[rc.gender]
        if lc.gender != r_gender:
            raise ValueError("Incompatible genders: %s - %s" % (
                lc.gender, rc.gender
            ))
        # Check directions are compatible
        if ((lc.direction == "i" and rc.direction != "o") or
                (lc.direciton == "o" and rc.direction != "i") or
                (lc.direciton == "s" and rc.direciton != "s")):
            raise ValueError("Incompatible direcitons: %s - %s" % (
                lc.direction, rc.direction))
        # Check types are compatible
        c_types = lc.type.get_compatible_types(lc.gender)
        if rc.type not in c_types:
            raise ValueError("Incompatible connection types: %s - %s" % (
                lc.type.name, rc.type.name
            ))
        # Check existing connecitons
        if (lc.type.genders in ("s", "m", "f", "mf") and
            self.get_p2p_connection(name)[0] is not None):
            raise ValueError("Already connected")
        # Create connection
        c = ObjectConnection(
            connection=[
                ObjectConnectionItem(object=self, connection=name),
                ObjectConnectionItem(object=remote_object,
                                     connection=remote_name)
            ],
            data=data
        ).save()
        return c


## Avoid circular references
from objectconnection import ObjectConnection, ObjectConnectionItem