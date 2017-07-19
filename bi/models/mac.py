# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# MAC Model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict
# NOC modules
from noc.core.clickhouse.model import Model
from noc.core.clickhouse.fields import (
    DateField, DateTimeField, UInt64Field, UInt16Field, UInt8Field,
    StringField, ReferenceField)
from noc.core.clickhouse.engines import MergeTree
from noc.core.bi.dictionaries.managedobject import ManagedObject
from noc.core.bi.dictionaries.interfaceprofile import InterfaceProfile
from noc.core.bi.dictionaries.networksegment import NetworkSegment
from noc.core.translation import ugettext as _


class MAC(Model):
    """
    MAC address table snapshot

    Common queries:

    Last seen MAC location:

    SELECT timestamp, object, interface
    FROM mac
    WHERE
      date >= ?
      AND mac = ?
       AND uni = 1
    ORDER BY timestamp DESC LIMIT 1;

    All MAC locations for date interval:

    SELECT timestamp, object, interface
    FROM mac
    WHERE
      date >= ?
      AND mac = ?
      AND uni = 1;
    """

    class Meta:
        db_table = "mac"
        engine = MergeTree("date", ("ts", "managed_object"))

    date = DateField(description=_("Date"))
    ts = DateTimeField(description=_("Created"))
    managed_object = ReferenceField(
        ManagedObject,
        description=_("Object Name")
    )
    mac = UInt64Field(description=_("MAC"))
    interface = StringField(description=_("Interface"))
    interface_profile = ReferenceField(
        InterfaceProfile,
        description=_("Interface Profile")
    )
    segment = ReferenceField(
        NetworkSegment,
        description=_("Network Segment")
    )
    vlan = UInt16Field(description=_("VLAN"))
    is_uni = UInt8Field(description=_("Is UNI"))

    def get_neighbors_by_mac(self, macs, mos=None):
        """
        Return list BI ID MO by interfaces. Filter mo by macs
        :param macs: list(int)
        :param mos: list(int)
        :return: Dict {mo_a: {iface1: [mo1, mo2], iface2: [mo3, mo4], ...}, mo_b: ...}
        """
        if not macs and not mos:
            return
        neighbors = defaultdict(dict)
        fields = [{"expr": "max(ts)", "alias": "timestamp", "order": 0},
                  {"expr": "mac", "alias": "mac", "group": 1},
                  {"expr": "vlan", "alias": "vlan", "group": 2},
                  {"expr": "managed_object", "alias": "managed_object", "group": 3},
                  {"expr": "interface", "alias": "interface", "group": 4}
                  ]
        if mos:
            res = self.query(
                {"fields": fields, "filter": {"$in": [{"$field": 'managed_object'}, mos]}})
        else:
            res = self.query(
                {"fields": fields, "filter": {"$in": [{"$field": 'mac'}, macs]}})

        for r in res["result"]:
            val = dict(zip(res["fields"], r))
            agg = int(val["managed_object"])
            if val["interface"] in neighbors[agg]:
                neighbors[agg][val["interface"]] += [int(val["mac"])]
            else:
                neighbors[agg][val["interface"]] = [int(val["mac"])]

        return neighbors
