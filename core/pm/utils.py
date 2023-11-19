# ----------------------------------------------------------------------
# PM Utils
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from collections import defaultdict
from typing import Iterable, Union, Tuple, Dict, Optional, DefaultDict, Any, List
import itertools

# Third-party modules
import orjson

# NOC modules
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.core.clickhouse.connect import connection as ch_connection
from noc.core.clickhouse.error import ClickhouseError
from noc.pm.models.metricscope import MetricScope
from noc.pm.models.metrictype import MetricType


def get_objects_metrics(
    managed_objects: Union[Iterable, int]
) -> Tuple[
    Dict["ManagedObject", Dict[str, Dict[str, int]]], Dict["ManagedObject", datetime.datetime]
]:
    """

    :param managed_objects:
    :return: Dictionary ManagedObject -> Path -> MetricName -> value
    """
    if not isinstance(managed_objects, Iterable):
        managed_objects = [managed_objects]

    # Object Metrics
    bi_map = {str(getattr(mo, "bi_id", mo)): mo for mo in managed_objects}
    query_interval = (
        ManagedObjectProfile.get_max_metrics_interval(
            set(mo.object_profile.id for mo in ManagedObject.objects.filter(bi_id__in=list(bi_map)))
        )
        * 2
    )
    from_date = datetime.datetime.now() - datetime.timedelta(seconds=max(query_interval, 3600))
    from_date = from_date.replace(microsecond=0)

    # @todo Left Join
    object_profiles = set(
        mo.object_profile.id for mo in ManagedObject.objects.filter(bi_id__in=list(bi_map))
    )
    msd: Dict[str, str] = {}  # Map ScopeID -> TableName
    labels_table = set()
    for ms in MetricScope.objects.filter():
        msd[ms.id] = ms.table_name
        if ms.labels:
            labels_table.add(ms.table_name)
    mts: Dict[str, Tuple[str, str, str]] = {
        str(mt.id): (msd[mt.scope.id], mt.field_name, mt.name) for mt in MetricType.objects.all()
    }  # Map Metric Type ID -> table_name, column_name, MetricType Name
    mmm = set()
    op_fields_map: DefaultDict[str, List[str]] = defaultdict(list)
    for op in ManagedObjectProfile.objects.filter(id__in=object_profiles):
        if not op.metrics:
            continue
        for mt in op.metrics:
            mmm.add(mts[mt["metric_type"]])
            op_fields_map[op.id] += [mts[mt["metric_type"]][1]]

    ch = ch_connection()
    mtable = []  # mo_id, mac, iface, ts
    metric_map = {}
    last_ts: Dict["ManagedObject", datetime.datetime] = {}  # mo -> ts

    for table, fields in itertools.groupby(sorted(mmm, key=lambda x: x[0]), key=lambda x: x[0]):
        fields = list(fields)
        SQL = """SELECT managed_object, argMax(ts, ts), %%s %s
              FROM %s
              WHERE
                date >= toDate('%s')
                AND ts >= toDateTime('%s')
                AND managed_object IN (%s)
              GROUP BY managed_object %%s
              """ % (
            ", ".join(["argMax(%s, ts) as %s" % (f[1], f[1]) for f in fields]),
            table,
            from_date.date().isoformat(),
            from_date.isoformat(sep=" "),
            ", ".join(bi_map),
        )
        if table in labels_table:
            # SQL = SQL % ("arrayStringConcat(labels, '|') as ll,", ", labels")
            SQL = SQL % (
                "arrayStringConcat(arrayMap(x -> splitByString('::', x)[-1], labels), '|') as labels,",
                ", labels",
            )
        else:
            SQL = SQL % ("", "")
        try:
            for result in ch.execute(post=SQL):
                if table in labels_table:
                    mo_bi_id, ts, labels = result[:3]
                    result = result[3:]
                else:
                    mo_bi_id, ts = result[:2]
                    labels, result = "", result[2:]
                mo = bi_map.get(mo_bi_id)
                i = 0
                for r in result:
                    f_name = fields[i][2]
                    mtable += [[mo, ts, labels, r]]
                    if mo not in metric_map:
                        metric_map[mo] = defaultdict(dict)
                    metric_map[mo][labels][f_name] = r
                    last_ts[mo] = max(ts, last_ts.get(mo, ts))
                    i += 1
        except ClickhouseError as e:
            print(e)
    return metric_map, last_ts


def get_interface_metrics(
    managed_objects: Union[Iterable, int], metrics: Optional[Dict[str, Any]] = None
) -> Tuple[
    Dict["ManagedObject", Dict[str, Dict[str, Union[float, int]]]],
    Dict["ManagedObject", datetime.datetime],
]:
    """

    :param managed_objects: ManagedObject list or bi_id list
    :param metrics: For customization getting metrics
    :return: Dictionary ManagedObject -> Path -> MetricName -> value
    """

    # mo = self.object
    if metrics and "map" not in metrics:
        return defaultdict(dict), {}
    elif not metrics:
        metrics = {
            "table_name": "interface",
            "map": {
                "load_in": "Interface | Load | In",
                "load_out": "Interface | Load | Out",
                "errors_in": "Interface | Errors | In",
                "errors_out": "Interface | Errors | Out",
            },
        }
    if not isinstance(managed_objects, Iterable):
        managed_objects = [managed_objects]
    bi_map: Dict[str, "ManagedObject"] = {
        str(getattr(mo, "bi_id", mo)): mo for mo in managed_objects
    }
    query_interval: float = (
        ManagedObjectProfile.get_max_metrics_interval(
            set(mo.object_profile.id for mo in ManagedObject.objects.filter(bi_id__in=list(bi_map)))
        )
        * 1.5
    )
    from_date = datetime.datetime.now() - datetime.timedelta(seconds=max(query_interval, 3600))
    from_date = from_date.replace(microsecond=0)
    requested_metrics = []
    metric_fields = {}
    for alias, mt in metrics["map"].items():
        mt = MetricType.get_by_name(mt)
        if not mt:
            continue
        metric_fields[alias] = mt.field_name
        requested_metrics += [f"argMax({mt.field_name}, ts) as {alias}"]
    SQL = """SELECT managed_object, argMax(ts, ts) as tsm,  splitByString('::', arrayFirst(x -> startsWith(x, 'noc::interface::'), labels))[-1] as iface, labels, %s
            FROM %s
            WHERE
              date >= toDate('%s')
              AND ts >= toDateTime('%s')
              AND managed_object IN (%s)
              AND NOT arrayExists(x -> startsWith(x, 'noc::subinterface::'), labels)
            GROUP BY managed_object, labels
            FORMAT JSON
            """ % (
        ", ".join(requested_metrics),
        metrics["table_name"],
        from_date.date().isoformat(),
        from_date.isoformat(sep=" "),
        ", ".join(bi_map),
    )
    ch = ch_connection()
    metric_map: DefaultDict["ManagedObject", Dict[str, Dict[str, Union[int, float]]]] = defaultdict(
        dict
    )
    last_ts: Dict["ManagedObject", datetime.datetime] = {}  # mo -> ts
    try:
        results = ch.execute(post=SQL, return_raw=True)
        results = orjson.loads(results)
    except ClickhouseError:
        results = {"data": []}
    for result in results["data"]:
        mo_bi_id, ts, iface = result["managed_object"], result["tsm"], result["iface"]
        mo = bi_map.get(mo_bi_id)
        if len(result["labels"]) == 1 and iface in metric_map[mo]:
            # If only interface metric
            continue
        metric_map[mo][iface] = {}
        for field in metric_fields.keys():
            metric_map[mo][iface][field] = result.get(field, 0.0)
            last_ts[mo] = max(ts, last_ts.get(mo, ts))
    return metric_map, last_ts


def get_dict_interface_metrics(
    managed_objects: Union[Iterable["ManagedObject"], "ManagedObject"]
) -> Dict[str, Dict[str, Union[str, Dict[str, str]]]]:
    """
    Get field_name and name from metric_type for interface.
    :param managed_objects:
    :return:
    meric_map = {
            "mo_name":{
                "table_name": "interface",
                "map": {
                    "load_in": "Interface | Load | In",
                    "load_out": "Interface | Load | Out",
                    "errors_in": "Interface | Errors | In",
                    "errors_out": "Interface | Errors | Out",
                }
            }
        }
    """
    # Avoid circular references
    meric_map = {}
    if not isinstance(managed_objects, Iterable):
        managed_objects = [managed_objects]

    for mo in managed_objects:
        meric_map[mo] = {"table_name": "interface", "map": _get_dict_interface_metrics(mo)}
    return meric_map


def _get_dict_interface_metrics(
    managed_object: ["ManagedObject"],
) -> Dict[str, Union[str, Dict[str, str]]]:
    """
    :return:
    {
                "load_in": "Interface | Load | In",
                "load_out": "Interface | Load | Out",
                "errors_in": "Interface | Errors | In",
                "errors_out": "Interface | Errors | Out",
            }
    """
    # Avoid circular references
    from noc.inv.models.interface import Interface
    from noc.inv.models.interfaceprofile import InterfaceProfile

    i_profile = set()
    f_n = {}
    for i in Interface.objects.filter(managed_object=managed_object.id, type="physical"):
        i_profile.add(i.profile.id)
    if i_profile:
        metrics_type = set()
        for ip in InterfaceProfile.objects.filter(id__in=i_profile):
            for metric in ip.metrics:
                metrics_type.add(metric.metric_type)
        for mt in metrics_type:
            f_n[mt.field_name] = mt.name
    return f_n


# Avoid circular references
from noc.sa.models.managedobject import ManagedObject
