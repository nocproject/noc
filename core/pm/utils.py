# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# PM Utils
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from collections import defaultdict
import itertools
# NOC modules
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.core.clickhouse.connect import connection as ch_connection
from noc.core.clickhouse.error import ClickhouseError
from noc.pm.models.metricscope import MetricScope
from noc.pm.models.metrictype import MetricType


def get_objects_metrics(managed_objects):
    """

    :param managed_objects:
    :return:
    """
    # Object Metrics

    bi_map = {str(getattr(mo, "bi_id", mo)): mo for mo in managed_objects}
    query_interval = ManagedObjectProfile.get_max_metrics_interval() * 1.5
    from_date = datetime.datetime.now() - datetime.timedelta(seconds=query_interval or 3600)
    from_date = from_date.replace(microsecond=0)

    # @todo Left Join
    object_profiles = set(mo.object_profile.id for mo in ManagedObject.objects.filter(bi_id__in=bi_map.keys()))
    msd = {ms.id: ms.table_name for ms in MetricScope.objects.filter()}
    mts = {str(mt.id): (msd[mt.scope.id], mt.field_name, mt.name) for mt in MetricType.objects.all()}
    mmm = set()
    op_fields_map = defaultdict(list)
    for op in ManagedObjectProfile.objects.filter(id__in=object_profiles):
        for mt in op.metrics:
            mmm.add(mts[mt["metric_type"]])
            op_fields_map[op.id] += [mts[mt["metric_type"]][1]]

    ch = ch_connection()
    mtable = []  # mo_id, mac, iface, ts
    metric_map = defaultdict(dict)
    last_ts = {}  # mo -> ts

    for table, fields in itertools.groupby(sorted(mmm, key=lambda x: x[0]), key=lambda x: x[0]):
        fields = list(fields)
        SQL = """SELECT managed_object, argMax(ts, ts), %s
              FROM %s
              WHERE
                date >= toDate('%s')
                AND ts >= toDateTime('%s')
                AND managed_object IN (%s)
              GROUP BY managed_object
              """ % (", ".join(["argMax(%s, ts) as %s" % (f[1], f[1]) for f in fields]),
                     table,
                     from_date.date().isoformat(), from_date.isoformat(sep=" "),
                     ", ".join(bi_map))
        try:
            for result in ch.execute(post=SQL):
                mo_bi_id, ts = result[:2]
                mo = bi_map.get(mo_bi_id)
                i = 0
                for r in result[2:]:
                    f_name = fields[i][2]
                    mtable += [[mo, ts, r]]
                    metric_map[mo][f_name] = r
                    last_ts[mo] = max(ts, last_ts.get(mo, ts))
                    i += 1
        except ClickhouseError:
            pass
    return metric_map, last_ts


def get_interface_metrics(managed_objects):
    # mo = self.object
    bi_map = {str(getattr(mo, "bi_id", mo)): mo for mo in managed_objects}
    query_interval = ManagedObjectProfile.get_max_metrics_interval(
        ManagedObject.objects.filter(bi_id__in=bi_map.keys())
    ) * 1.5
    from_date = datetime.datetime.now() - datetime.timedelta(seconds=query_interval or 3600)
    from_date = from_date.replace(microsecond=0)

    SQL = """SELECT managed_object, arrayStringConcat(path) as iface, argMax(ts, ts), argMax(load_in, ts), argMax(load_out, ts), argMax(errors_in, ts), argMax(errors_out, ts)
            FROM interface
            WHERE
              date >= toDate('%s')
              AND ts >= toDateTime('%s')
              AND managed_object IN (%s)
            GROUP BY managed_object, iface
            """ % (from_date.date().isoformat(), from_date.isoformat(sep=" "),
                   ", ".join(bi_map))
    ch = ch_connection()
    mtable = []  # mo_id, mac, iface, ts
    metric_map = defaultdict(dict)
    last_ts = {}  # mo -> ts
    try:
        for mo_bi_id, iface, ts, load_in, load_out, errors_in, errors_out in ch.execute(post=SQL):
            mo = bi_map.get(mo_bi_id)
            if mo:
                mtable += [[mo, iface, ts, load_in, load_out]]
                metric_map[mo][iface] = {"load_in": int(load_in),
                                         "load_out": int(load_out),
                                         "errors_in": int(errors_in),
                                         "errors_out": int(errors_out)}
                last_ts[mo] = max(ts, last_ts.get(mo, ts))
    except ClickhouseError:
        pass
    return metric_map, last_ts
