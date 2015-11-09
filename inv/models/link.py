## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Link model
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from collections import defaultdict
import datetime
## Third-party modules
from mongoengine import signals
## NOC modules
from noc.lib.nosql import (Document, PlainReferenceListField,
                           StringField, DateTimeField)
from interface import Interface


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
