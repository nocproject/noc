# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ReportMetrics datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import six
import time
from collections import namedtuple, OrderedDict
# Third-party modules
# NOC modules
from .base import BaseReportColumn
from noc.core.clickhouse.connect import connection


class ReportMetrics(BaseReportColumn):
    CHUNK_SIZE = 10000
    TABLE_NAME = "noc.interface"
    ATTRS = OrderedDict([(a, "avg(%s)" % a) for a in ["load_in", "load_out", "packets_in", "packets_out",
                                                      "errors_in", "errors_out"]])
    KEY_FIELDS = OrderedDict([("iface_name", "path")])

    def __init__(self, mos_ids, f_date, to_date, columns=None):
        super(ReportMetrics, self).__init__(mos_ids)
        self.from_date = f_date
        self.to_date = to_date
        if columns and isinstance(columns, list):
            for c in set(self.ATTRS) - set(columns):
                self.ATTRS.pop(c)
        elif columns and isinstance(columns, OrderedDict):
            self.ATTRS = columns
        self.unknown_value = ([[""] * (len(self.ATTRS) + len(self.KEY_FIELDS))],)

    @staticmethod
    def get_mo_filter(ids, use_dictionary=False):
        return "managed_object IN (%s)" % ", ".join([str(c) for c in ids])

    def get_filter_cond(self):
        return {"q_where": [], "q_having": []}

    def get_query_ch(self, ids, from_date, to_date):
        def update_dict(d1, d2):
            for k in d2:
                if k in d1:
                    d1[k] += d2[k]
                else:
                    d1[k] = d2[k]
        ts_from_date = time.mktime(from_date.timetuple())
        ts_to_date = time.mktime(to_date.timetuple())
        def_map = {"q_select": ["managed_object"],
                   "q_where": [self.get_mo_filter(ids),
                               "(date >= toDate(%d)) AND (ts >= toDateTime(%d) AND ts <= toDateTime(%d))" %
                               (ts_from_date, ts_from_date, ts_to_date)],
                   "q_group": ["managed_object"],
                   "q_order_by": ["managed_object"]}
        if self.KEY_FIELDS:
            update_dict(def_map, {"q_select": ["%s AS %s" % (f, a) for a, f in six.iteritems(self.KEY_FIELDS)],
                                  "q_group": [x for x in six.itervalues(self.KEY_FIELDS)]})
        condition = self.get_filter_cond()
        if condition["q_having"]:
            update_dict(def_map, condition["q_having"])
        update_dict(def_map, {"q_select": ["%s AS %s" % (field, alias) for alias, field in six.iteritems(self.ATTRS)]})
        query = " ".join(["select %s" % ",".join(def_map["q_select"]),
                          "from %s" % self.TABLE_NAME,
                          "where %s" % " and ".join(def_map["q_where"]),
                          "group by %s" % ",".join(def_map["q_group"]),
                          "order by %s" % ",".join(def_map["q_order_by"])])
        return query

    def extract(self):
        # do_query_ch(self, moss, query_map, f_date, to_date)
        Metrics = namedtuple("Metrics", [x[1] for x in self.KEY_FIELDS] + self.ATTRS.keys())
        Metrics.__new__.__defaults__ = ("",) * len(Metrics._fields)

        client = connection()
        mo_ids = self.sync_ids[:]
        f_date, to_date = self.from_date, self.to_date
        current_mo, block = None, []
        while mo_ids:
            chunk, mo_ids = mo_ids[:self.CHUNK_SIZE], mo_ids[self.CHUNK_SIZE:]
            query = self.get_query_ch(chunk, f_date, to_date)
            # print(query)
            for row in client.execute(query):
                # print (row)
                if current_mo and row[0] != current_mo:
                    yield int(row[0]), block
                    block = []
                block += [Metrics(*row[1:])]
                current_mo = row[0]
            if current_mo and block:
                yield int(current_mo), block


class ReportCPUMetrics(ReportMetrics):
    TABLE_NAME = "noc.cpu"
    ATTRS = {"cpu_usage": "avg(usage)"}
    KEY_FIELDS = []


class ReportMemoryMetrics(ReportMetrics):
    TABLE_NAME = "noc.memory"
    ATTRS = {"memory_usage": "avg(usage)"}
    KEY_FIELDS = []


class ReportInterfaceFlapMetrics(ReportMetrics):
    """
    select dictGetString('managedobject', 'name',managed_object) as name,
    dictGetString('managedobject', 'address',managed_object) as address,
    path[-1],
    countEqual(arrayMap((a,p) -> a + p, arrayPushFront(groupArray(status_oper),groupArray(status_oper)[1]) ,arrayPushBack(groupArray(status_oper),groupArray(status_oper)[-1])), 1) as flap_count from interface where managed_object in (select bi_id from dictionaries.managedobject where adm_domain_id in ('364', '365', '366', '367', '368', '369', '370', '371', '372', '373', '374', '375', '363', '362', '26', '376', '377', '378', '379', '380', '474')) and date >= '2018-07-20' group by managed_object,path  having max(status_oper) = 1 and  min(status_oper) = 0 and countEqual(groupArray(status_oper), 1) > 10 and countEqual(groupArray(status_oper), 0) > 10 order by flap_count desc limit 20 FORMAT CSV;
    """
    TABLE_NAME = "noc.interface"
    ATTRS = OrderedDict({"dictGetString('managedobject', 'name', managed_object)": "name",
                         "dictGetString('managedobject', 'address',managed_object)": "address",
                         "countEqual(arrayMap((a,p) -> a + p, arrayPushFront(groupArray(status_oper),"
                         "groupArray(status_oper)[1]) ,arrayPushBack(groupArray(status_oper),"
                         "groupArray(status_oper)[-1])), 1)": "flap"})
    KEY_FIELDS = OrderedDict([("iface_name", "path[-1]")])

    def get_filter_cond(self):
        return {"q_having": ["max(status_oper) = 1",
                             "min(status_oper) = 0",
                             "countEqual(groupArray(status_oper), 1) > 10",
                             "countEqual(groupArray(status_oper), 0) > 10"]
                }
