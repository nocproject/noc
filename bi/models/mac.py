# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# MAC Model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict
import datetime
import six
# NOC modules
from noc.config import config
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

    class Meta(object):
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

    def mac_filter(self, query, offset=0, limit=400, convert_mac=False):
        """
        Filter interface to MACDB
        :param query: Query to MACDB
        :param query: dict
        :param offset: Offset output data
        :type offset: int
        :param limit: Offset output data
        :type limit: limit data count
        :param convert_mac: Conver MAC from int to str represent
        :return: list query result from MACDB
        select max(ts), managed_object, interface, vlan from mac
        where like(MACNumToString(mac), 'A0:AB:1B%') group by managed_object, interface, vlan;
        """
        query_field = ["mac", "managed_object"]
        t0 = datetime.datetime.now() - datetime.timedelta(seconds=config.web.macdb_window)
        t0 = t0.replace(microsecond=0)

        if not query:
            return

        f_filter = {"$and": [{"$gte": [{"$field": "date"}, t0.date().isoformat()]},
                             {"$gte": [{"$field": "ts"}, t0.isoformat(sep=" ")]}]}
        for k in query:
            field = k
            q = "eq"
            if "__" in field:
                field, q = k.split("__")
            if field not in query_field:
                # Not implemented
                continue
            if q == "like" and not convert_mac:
                field = "MACNumToString(mac)"
            # @todo convert mac all
            if isinstance(query[k], list) and len(query[k]) == 1:
                arg = query[k][0].strip()
            elif isinstance(query[k], six.string_types):
                arg = query[k].strip()
            else:
                arg = query[k]
            f_filter["$and"] += [{"$%s" % q: [{"$field": field}, arg]}]
        if not f_filter:
            return
        fields = [{"expr": "argMax(ts, ts)", "alias": "timestamp", "order": 0},
                  {"expr": "mac", "alias": "mac", "group": 1},
                  {"expr": "vlan", "alias": "vlan", "group": 2},
                  {"expr": "managed_object", "alias": "managed_object", "group": 3},
                  {"expr": "argMax(interface, ts)", "alias": "interface"}
                  ]
        if convert_mac:
            fields[1]["expr"] = "MACNumToString(mac)"
        # @todo paging (offset and limit)
        # @todo check in list
        ch_query = {"fields": fields, "filter": f_filter, "limit": limit}
        if offset:
            ch_query["offset"] = offset
        res = self.query(ch_query)
        # print res
        for r in res["result"]:
            yield dict(zip(res["fields"], r))

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
        if mos:
            query = {"managed_object__in": mos}
        else:
            query = {"mac__in": macs}
        for r in self.mac_filter(query):
            agg = int(r["managed_object"])
            if r["interface"] in neighbors[agg]:
                neighbors[agg][r["interface"]] += [int(r["mac"])]
            else:
                neighbors[agg][r["interface"]] = [int(r["mac"])]

        return neighbors

    def get_mac_history(self, mac):
        return []
