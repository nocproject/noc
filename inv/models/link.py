# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Link model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict
import datetime
# NOC modules
from noc.lib.nosql import (Document, PlainReferenceListField,
                           StringField, DateTimeField, ListField,
                           IntField)
from noc.core.model.decorator import on_delete, on_save


@on_delete
@on_save
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
        "strict": False,
        "indexes": ["interfaces", "linked_objects"]
    }

    interfaces = PlainReferenceListField("inv.Interface")
    # List of linked objects
    linked_objects = ListField(IntField())
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
        return u"(%s)" % ", ".join([unicode(i) for i in self.interfaces])

    def clean(self):
        self.linked_objects = sorted(set(i.managed_object.id for i in self.interfaces))
        super(Link, self).clean()

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
        return len(self.linked_objects) == 2

    @property
    def is_lag(self):
        """
        Check link is unresolved LAG
        :return:
        """
        if self.is_ptp:
            return True
        d = defaultdict(int)  # object -> count
        for i in self.interfaces:
            d[i.managed_object.id] += 1
        if len(d) != 2:
            return False
        k = d.keys()
        return d[k[0]] == d[k[1]]

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
        if not self.is_ptp:
            return False
        i1, i2 = self.interfaces
        return i1.managed_object == i2.managed_object

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
        from interface import Interface
        ifaces = Interface.objects.filter(managed_object=object.id).values_list("id")
        return cls.objects.filter(interfaces__in=ifaces)

    @classmethod
    def object_links_count(cls, object):
        return cls.object_links(object).count()

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
        return list(set(i.managed_object for i in self.interfaces))

    def update_topology(self):
        for mo in self.managed_objects:
            mo.update_topology()
