# ----------------------------------------------------------------------
# ReportMetrics datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import time
from collections import namedtuple, OrderedDict

# NOC modules
from noc.core.clickhouse.connect import connection
from .base import BaseReportColumn


class ReportMetrics(BaseReportColumn):
    CHUNK_SIZE = 1000
    TABLE_NAME = None
    SELECT_QUERY_MAP = {
        # (List#, Name, Alias): TypeNormalizer or (TypeNormalizer, DefaultValue)
    }
    # KEY_FIELDS = OrderedDict([("iface_name", "path")])
    CUSTOM_FILTER = {"having": [], "where": []}
    KEY_FIELDS = None

    def __init__(self, mos_ids, f_date, to_date, columns=None):
        super().__init__(mos_ids)
        self.from_date = f_date
        self.to_date = to_date
        self.ch_client = connection()
        if not (self.TABLE_NAME and self.SELECT_QUERY_MAP):
            raise NotImplementedError
        if columns and isinstance(columns, list):
            for c in set(self.ATTRS) - set(columns):
                self.ATTRS.pop(c)
        elif columns and isinstance(columns, OrderedDict):
            self.ATTRS = columns
        self.unknown_value = ([[""] * (len(self.SELECT_QUERY_MAP) + len(self.KEY_FIELDS))],)

    @staticmethod
    def get_mo_filter(ids, use_dictionary=False):
        return "managed_object IN (%s)" % ", ".join([str(c) for c in ids])

    def get_custom_conditions(self):
        return self.CUSTOM_FILTER

    def get_query_ch(self, from_date, to_date):
        ts_from_date = time.mktime(from_date.timetuple())
        ts_to_date = time.mktime(to_date.timetuple())
        custom_conditions = self.get_custom_conditions()
        def_map = {
            "q_select": [],
            "q_where": [
                "%s",
                "(date >= toDate(%d)) AND (ts >= toDateTime(%d) AND ts <= toDateTime(%d))"
                % (ts_from_date, ts_from_date, ts_to_date),
                *custom_conditions["where"][:],
            ],
            "q_group": self.KEY_FIELDS,
            "q_having": custom_conditions["having"][:],
            "q_order_by": self.KEY_FIELDS,
        }
        for num, field, alias in sorted(self.SELECT_QUERY_MAP, key=lambda x: x[0]):
            func = self.SELECT_QUERY_MAP[(num, field, alias)] or "avg(%s)" % field
            def_map["q_select"] += ["%s AS %s" % (func, alias or "a_" + field)]
        return " ".join(
            [
                "SELECT %s" % ",".join(def_map["q_select"]),
                "FROM %s" % self.TABLE_NAME,
                "WHERE %s" % " AND ".join(def_map["q_where"]),
                "GROUP BY %s" % ",".join(def_map["q_group"]),
                "HAVING %s" % " AND ".join(def_map["q_having"]) if def_map["q_having"] else "",
                "ORDER BY %s" % ",".join(def_map["q_order_by"]),
            ]
        )

    def do_query(self):
        mo_ids = self.sync_ids[:]
        f_date, to_date = self.from_date, self.to_date
        query = self.get_query_ch(f_date, to_date)
        while mo_ids:
            chunk, mo_ids = mo_ids[: self.CHUNK_SIZE], mo_ids[self.CHUNK_SIZE :]
            for row in self.ch_client.execute(query % self.get_mo_filter(chunk)):
                yield row

    def extract(self):
        # do_query_ch(self, moss, query_map, f_date, to_date)
        Metrics = namedtuple("Metrics", [x[1] for x in self.KEY_FIELDS] + list(self.ATTRS))
        Metrics.__new__.__defaults__ = ("",) * len(Metrics._fields)
        current_mo, block = None, []
        for row in self.do_query():
            # print (row)
            if current_mo and row[0] != current_mo:
                yield int(row[0]), block
                block = []
            block += [Metrics(*row[1:])]
            block = row[1:]
            current_mo = row[0]
            if current_mo and block:
                yield int(current_mo), block


class ReportInterfaceMetrics(ReportMetrics):
    TABLE_NAME = "noc.interface"
    SELECT_QUERY_MAP = {
        # (List#, Name, Alias): TypeNormalizer or (TypeNormalizer, DefaultValue)
        # Column#, db_name, column_alias, query
        (0, "managed_object", None): "",
        (1, "path", "iface"): "arrayStringConcat(path)",
        (2, "load_in", "l_in"): "round(quantile(0.90)(load_in), 0)",
        (3, "load_in", "load_in_p"): "",
        (4, "load_out", None): "",
        (5, "load_out", "load_out_p"): "",
        (6, "packets_in", None): "",
        (7, "packets_out", None): "",
        (8, "errors_in", None): "",
        (9, "errors_out", None): "",
        (10, "speed", None): "",
    }
    # KEY_FIELDS = OrderedDict([("iface_name", "path")])
    KEY_FIELDS = ("managed_object", "path")


class ReportCPUMetrics(ReportMetrics):
    TABLE_NAME = "noc.cpu"
    SELECT_QUERY_MAP = {(0, "managed_object", None): "", (1, "usage", "cpu_usage"): ""}
    KEY_FIELDS = ["managed_object", "path"]


class ReportMemoryMetrics(ReportMetrics):
    TABLE_NAME = "noc.memory"
    SELECT_QUERY_MAP = {(0, "managed_object", None): "", (1, "usage", "memory_usage"): ""}
    KEY_FIELDS = ["managed_object", "path"]


class ReportPingMetrics(ReportMetrics):
    TABLE_NAME = "noc.ping"
    SELECT_QUERY_MAP = {(0, "managed_object", None): "", (1, "avg(rtt)", "ping_rtt"): ""}
    KEY_FIELDS = ["managed_object"]
