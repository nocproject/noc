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
    KEY_FIELDS = ["path"]
    # QUERY_MAP = {["avg(%s) AS %s" % (self.select_column[field], field) for field in ATTRS[1:]]}
    unknown_value = ([""] * len(ATTRS.keys()),)

    def __init__(self, mos_ids, f_date, to_date):
        super(ReportMetrics, self).__init__(mos_ids)
        self.from_date = f_date
        self.to_date = to_date
        self.unknown_value = ([""] * len(self.ATTRS),)
        # self.select_column = [a: "avg(%s)" % a for a in six.iteritems(report_column)]
        #  else:
        #    self.select_column = {["avg(%s) AS %s" % (self.select_column[field], field) for field in self.ATTRS[1:]]}
        #     self.select_column = ["avg(%s) AS %s" % (field, field) for field in self.ATTRS[1:]]

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
                   "q_from": [],  # q_from = "from %s" % map_table[reporttype]
                   "q_where": ["managed_object IN (%s)",
                               "(date >= toDate(%d)) AND (ts >= toDateTime(%d) AND ts <= toDateTime(%d))" %
                               (ts_from_date, ts_from_date, ts_to_date)],
                   "q_group": ["managed_object"],
                   "q_order_by": ["managed_object"]}
        if self.KEY_FIELDS:
            update_dict(def_map, {"q_select": self.KEY_FIELDS,
                                  "q_group": self.KEY_FIELDS})
        update_dict(def_map, {"q_select": ["%s AS %s" % (field, alias) for alias, field in six.iteritems(self.ATTRS)]})
        query = " ".join(["select %s" % ",".join(def_map["q_select"]),
                          "from %s" % self.TABLE_NAME,
                          "where %s" % " and ".join(def_map["q_where"]),
                          "group by %s" % ",".join(def_map["q_group"]),
                          "order by managed_object"])
        return query % ", ".join([str(c) for c in ids])

    def extract(self):
        # do_query_ch(self, moss, query_map, f_date, to_date)
        Metrics = namedtuple("Metrics", self.KEY_FIELDS + self.ATTRS.keys())
        Metrics.__new__.__defaults__ = ("",) * len(Metrics._fields)

        client = connection()
        mo_ids = self.sync_ids[:]
        f_date, to_date = self.from_date, self.to_date
        current_mo, block = None, []
        while mo_ids:
            chunk, mo_ids = mo_ids[:self.CHUNK_SIZE], mo_ids[self.CHUNK_SIZE:]
            query = self.get_query_ch(chunk, f_date, to_date)
            print(query)
            for row in client.execute(query):
                print (row)
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
