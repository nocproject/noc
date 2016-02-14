## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Link model
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from collections import defaultdict
import datetime
## NOC modules
from noc.lib.nosql import (Document, PlainReferenceListField,
                           StringField, DateTimeField)
from interface import Interface
from noc.core.model.decorator import on_delete, on_save
from noc.core.defer import call_later


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
        "allow_inheritance": False,
        "indexes": ["interfaces"]
    }

    interfaces = PlainReferenceListField(Interface)
    # Name of discovery method or "manual"
    discovery_method = StringField()
    # Timestamp of first discovery
    first_discovered = DateTimeField(default=datetime.datetime.now)
    # Timestamp of last confirmation
    last_seen = DateTimeField()

    def __unicode__(self):
        return u"(%s)" % ", ".join([unicode(i) for i in self.interfaces])

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
        return len(self.interfaces) == 2

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
        self.last_seen = datetime.datetime.now()
        if method:
            self.discovery_method = method
        self.save()

    @classmethod
    def object_links(cls, object):
        ifaces = Interface.objects.filter(managed_object=object.id).values_list("id")
        return cls.objects.filter(interfaces__in=ifaces)

    @classmethod
    def object_links_count(cls, object):
        ifaces = Interface.objects.filter(managed_object=object.id).values_list("id")
        return cls.objects.filter(interfaces__in=ifaces).count()

    def on_save(self):
        self.update_pop_links()
        self.update_segments()

    def on_delete(self):
        self.update_pop_links()
        self.update_segments()

    def update_pop_links(self):
        for i in self.interfaces:
            for o in Object.get_managed(i.managed_object):
                pop = o.get_pop()
                if not pop and i.managed_object.container:
                    # Fallback to MO container
                    pop = i.managed_object.container.get_pop()
                if pop:
                    call_later(
                        "noc.inv.util.pop_links.update_pop_links",
                        20,
                        pop_id=pop.id
                    )

    def update_segments(self):
        segments = set()
        for i in self.interfaces:
            segments.add(i.managed_object.segment.id)
        for s in segments:
            call_later(
                "noc.core.topology.segment.update_uplinks",
                60,
                segment_id=s
            )


##
from object import Object
