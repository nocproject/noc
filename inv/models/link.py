<<<<<<< HEAD
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Link model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict
import datetime
# NOC modules
from noc.lib.nosql import (Document, PlainReferenceListField,
                           StringField, DateTimeField, ListField,
                           IntField, ObjectIdField)
from noc.core.model.decorator import on_delete, on_save


@on_delete
@on_save
=======
## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Link model
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from collections import defaultdict
## Third-party modules
from mongoengine import signals
## NOC modules
from noc.lib.nosql import Document, PlainReferenceListField, StringField
from interface import Interface


>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
class Link(Document):
    """
    Network links.
    Always contains a list of 2*N references.
    2 - for fully resolved links
    2*N for unresolved N-link portchannel
    N, N > 2 - broadcast media
    """
    meta = {
        "collection": "noc.links",
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            "interfaces",
            "linked_objects",
            "linked_segments"
        ]
    }

    # Optional link name
    name = StringField()
    # Optional description
    description = StringField()
    # Optional shape
    shape = StringField()
    # List of interfaces
    interfaces = PlainReferenceListField("inv.Interface")
    # Link type, detected automatically
    type = StringField(choices=[
        # 2 managed objects, 2 linked interfaces
        ("p", "Point-to-Point"),
        # 2 managed objects, even number of linked interfaces (>2)
        ("a", "Point-to-Point Aggregated"),
        # >2 managed objects, one uplink
        ("m", "Point-to-Multipoint"),
        # >2 managed objects, no dedicated uplink
        ("M", "Multipoint-to-Multipoint"),
        # Unknown
        ("u", "Unknown")
    ], default="u")
    # List of linked objects
    linked_objects = ListField(IntField())
    # List of linked segments
    linked_segments = ListField(ObjectIdField())
    # Name of discovery method or "manual"
    discovery_method = StringField()
    # Timestamp of first discovery
    first_discovered = DateTimeField(default=datetime.datetime.now)
    # Timestamp of last confirmation
    last_seen = DateTimeField()
    # L2 path cost
    l2_cost = IntField(default=1)
    # L3 path cost
    l3_cost = IntField(default=1)

    def __unicode__(self):
        return u"(%s)" % ", ".join(unicode(i) for i in self.interfaces)

    def clean(self):
        self.linked_objects = sorted(set(i.managed_object.id for i in self.interfaces))
        self.linked_segments = sorted(set(i.managed_object.segment.id for i in self.interfaces))
        self.type = self.get_type()
=======
        "allow_inheritance": False,
        "indexes": ["interfaces"]
    }

    interfaces = PlainReferenceListField(Interface)
    discovery_method = StringField()

    def __unicode__(self):
        return u"(%s)" % ", ".join([unicode(i) for i in self.interfaces])
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def contains(self, iface):
        """
        Check link contains interface
        :return: boolean
        """
        return iface in self.interfaces

    @property
    def is_ptp(self):
        """
        Check link is point-to-point link
        :return:
        """
<<<<<<< HEAD
        return self.type == "p" or self.type == "a"
=======
        return len(self.interfaces) == 2
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    @property
    def is_lag(self):
        """
        Check link is unresolved LAG
        :return:
        """
<<<<<<< HEAD
        return self.type == "p" or self.type == "a"
=======
        if self.is_ptp:
            return True
        d = defaultdict(int)  # object -> count
        for i in self.interfaces:
            d[i.managed_object.id] += 1
        if len(d) != 2:
            return False
        k = d.keys()
        return d[k[0]] == d[k[1]]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    @property
    def is_broadcast(self):
        """
        Check link is broadcast media
        :return:
        """
        return not self.is_ptp and not self.is_lag

    @property
    def is_loop(self):
        """
        Check link is looping to same object
        :return:
        """
<<<<<<< HEAD
        return len(self.linked_objects) == 1

    @property
    def interface_ids(self):
        """
        Returns list of interface ids, avoiding dereference
        :return:
        """
        def q(i):
            if hasattr(i, "id"):
                return i.id
            return i

        return [q(iface) for iface in self._data.get("interfaces", [])]
=======
        if not self.is_ptp:
            return False
        i1, i2 = self.interfaces
        return i1.managed_object == i2.managed_object
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def other(self, interface):
        """
        Return other interfaces of the link
        :param interface:
        :return:
        """
        return [i for i in self.interfaces if i.id != interface.id]

    def other_ptp(self, interface):
        """
        Return other interface of ptp link
        :param interface:
        :return:
        """
        return self.other(interface)[0]

<<<<<<< HEAD
    def touch(self, method=None):
        """
        Touch last_seen
        """
        now = datetime.datetime.now()
        op = {
            "last_seen": now
        }
        self.last_seen = now
        if method:
            self.discovery_method = method
            op["discovery_method"] = method
        # Do not save to prevent rebuilding topology
        self._get_collection().update({
            "_id": self.id
        }, {
            "$set": op
        })
        # self.save()

    @classmethod
    def object_links(cls, object):
        return Link.objects.filter(linked_objects=object.id)

    @classmethod
    def object_links_count(cls, object):
        return Link.objects.filter(linked_objects=object.id).count()

    def on_save(self):
        if not hasattr(self, "_changed_fields") or "interfaces" in self._changed_fields:
            self.update_topology()

    def on_delete(self):
        self.update_topology()

    @property
    def managed_objects(self):
        """
        List of connected managed objects
        """
        from noc.sa.models.managedobject import ManagedObject
        return list(ManagedObject.objects.filter(id__in=self.linked_objects))

    @property
    def segments(self):
        """
        List of segments connected by link
        :return:
        """
        from noc.inv.models.networksegment import NetworkSegment
        return list(NetworkSegment.objects.filter(id__in=self.linked_segments))

    def update_topology(self):
        for mo in self.managed_objects:
            mo.update_topology()

    def get_type(self):
        """
        Detect link type
        :return: Link type as value for .type
        """
        n_objects = len(self.linked_objects)
        n_interfaces = len(self.interfaces)
        if n_objects == 2 and n_interfaces == 2:
            return "p"  # Point-to-point
        if n_objects == 2 and n_interfaces > 2 and n_interfaces % 2 == 0:
            d = defaultdict(int)  # object -> count
            for i in self.interfaces:
                d[i.managed_object.id] += 1
            k = d.keys()
            if d[k[0]] == d[k[1]]:
                return "a"  # Point-to-Point aggregated
        if n_objects > 2:
            if self.type == "m":
                return "m"
            else:
                return "M"
        return "u"
=======
    @classmethod
    def object_links(cls, object):
        ifaces = Interface.objects.filter(managed_object=object.id).values_list("id")
        return cls.objects.filter(interfaces__in=ifaces)

    @classmethod
    def object_links_count(cls, object):
        ifaces = Interface.objects.filter(managed_object=object.id).values_list("id")
        return cls.objects.filter(interfaces__in=ifaces).count()

    @classmethod
    def _update_pop_links(cls, sender, document, target=None, **kwargs):
        for i in document.interfaces:
            for o in Object.get_managed(i.managed_object):
                pop = o.get_pop()
                if pop:
                    refresh_schedule(
                        "main.jobs", "inv.update_pop_links",
                        key=pop.id, delta=5)


signals.pre_delete.connect(Link._update_pop_links, sender=Link)
signals.post_save.connect(Link._update_pop_links, sender=Link)


##
from object import Object
from noc.lib.scheduler.utils import refresh_schedule
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
