# ----------------------------------------------------------------------
# PM Utils
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from collections import defaultdict
from typing import Iterable, Union, Tuple, Dict, Optional, DefaultDict, Any, List, Set
import itertools

# Third-party modules
import orjson

# NOC modules
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.core.clickhouse.connect import connection as ch_connection
from noc.core.clickhouse.error import ClickhouseError
from noc.pm.models.metricscope import MetricScope
from noc.pm.models.metrictype import MetricType
from noc.models import get_model


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


# metric.cpu.usage(managed_object="ЦАТС-102-61#1000006")

MetricKey = Tuple[str, Tuple[Tuple[str, Any], ...], Tuple[str, ...]]


class MetricValue:
    """
    Metric Value class. Return value when call
    # def humanize
    """

    def __init__(self, proxy: "MetricScopeProxy", metric_type):
        self.metric_proxy = proxy
        self.metric_type: "MetricType" = metric_type
        self.function = "last"
        # Start and stop ts

    @property
    def alias(self) -> str:
        """
        Metric value alias, union by field_name and agg function
        """
        return self.metric_type.field_name

    @property
    def query(self) -> str:
        """
        Expression for query metric value
        """
        return f"argMax({self.metric_type.field_name}, ts)"

    def __call__(self, *args, **kwargs) -> float:
        """
        scale = convert value by scale
        """
        print("Call MetricValue", args, kwargs)
        r = self.metric_proxy.query_metrics([self], **kwargs)
        # return self.__call__(managed_object="ЦАТС-102-61#1000006")
        return r.get(self.metric_type.field_name)

    def __getattr__(self, item) -> "MetricValue":
        """
        humanize - return str value
        """
        if self.function:
            return self
        self.function = item
        return self


class MetricScopeProxy:
    """
    Proxy Metric Scale

    # Call for multiple fields (cpu_load, cpu_usage).multi
    # metric.cpu.load_in.load_out.sum
    """

    def __init__(self, scope: Optional["MetricScope"] = None):
        self.scope: "MetricScope" = scope
        self.metric_keys: Set[MetricKey] = set()
        self.metric_cache: Dict[MetricKey, float] = {}
        self.metric_requests: Dict[str, MetricValue] = {}
        self.current_metric_key: Optional[MetricKey] = None

    def get_metric_key(self, **kwargs) -> "MetricKey":
        keys = []
        for k in self.scope.key_fields:
            if k.field_name in kwargs:
                # Resolve object if f.field_name__ in kwargs
                keys.append((k.field_name, int(kwargs[k.field_name])))
        for ll in self.scope.labels:
            if ll.field_name in kwargs:
                keys.append((ll.field_name, f"'{str(kwargs[ll.field_name])}'"))
        if "labels" in kwargs:
            labels = tuple(kwargs["labels"])
        else:
            labels = tuple([])
        return "*", tuple(keys), labels

    def resolve_object(self, model_id, ids) -> List[str]:
        r = []
        if not isinstance(ids, list):
            ids = [ids]
        m = get_model(model_id)
        for ii in ids:
            if isinstance(ii, int):
                r.append(str(ii))
                continue
            o = m.objects.filter(name=ii).first()
            r.append(str(o.bi_id))
        return r

    def get_query(self, req_metrics: List[MetricValue], **kwargs) -> str:
        fields, group_by = [], set()
        conditions = defaultdict(list)
        for mk in self.metric_keys:
            _, keys, labels = mk
            key, values = [], []
            for field, value in keys:
                if (field, field) not in fields:
                    fields.append((field, field))
                group_by.add(field)
                key.append(field)
                values.append(str(value))
            # @todo labels
            conditions[tuple(key)].append("(%s)" % ", ".join(values))
        where = []
        for cond, values in conditions.items():
            where += [" (%s) IN (%s)" % (", ".join(cond), ", ".join(values))]
        for m in req_metrics:
            fields.append((m.query, m.alias))
        SQL = """
              SELECT argMax(ts, ts), %s
              FROM %s
              WHERE
              date >= %%s
              AND ts >= %%s
              AND (%s)
              GROUP BY %s
              FORMAT JSONEachRow
              """ % (
            ", ".join(f"{query} as {alias}" for query, alias in fields),
            self.scope.table_name,
            " OR ".join(where),
            ", ".join(list(group_by)),
        )
        return SQL

    def query_metrics(self, req_metrics: List[MetricValue], **kwargs) -> Dict[str, float]:
        """
        Gettinig metrics from database
        """
        if kwargs:
            _, keys, labels = self.get_metric_key(**kwargs)
        elif self.current_metric_key:
            _, keys, labels = self.current_metric_key
        else:
            raise ValueError("Not selected Object for request metrics")
        r: Dict[str, float] = {}
        for m in req_metrics:
            print((m.alias, keys, labels) in self.metric_cache)
            if (m.alias, keys, labels) in self.metric_cache:
                r[m.alias] = self.metric_cache[(m.alias, keys, labels)]
        if r:
            return r
        ch = ch_connection()
        from_date = datetime.datetime.now().replace(microsecond=0) - datetime.timedelta(hours=2)
        query = self.get_query(req_metrics, **kwargs)
        # print(query)
        result = ch.execute(
            sql=query,
            args=[from_date.date().isoformat(), from_date.isoformat(sep=" ")],
            return_raw=True,
        )
        # print(result)
        req_metrics = {m.alias for m in req_metrics}
        for row in result.splitlines():
            row = orjson.loads(row)
            _, keys, labels = self.get_metric_key(**row)
            for name, value in row.items():
                if name in req_metrics:
                    r[name] = value
                    self.metric_cache[(name, keys, labels)] = value
        if r is None:
            raise ValueError
        return r

    def __getattr__(self, item) -> Union["MetricValue", "MetricScopeProxy"]:
        # print("ProxyX", item)
        if self.scope and self.scope.table_name == item:
            return self
        elif not self.scope:
            self.scope = MetricScope.get_by_table_name(item)
            return self
        mt = MetricType.get_by_field_name(item, scope=self.scope.table_name)
        if not mt:
            raise AttributeError("[%s] Unknown metric: %s" % (self.scope.name, item))
        if mt.field_name in self.metric_requests:
            return self.metric_requests[mt.field_name]
        self.metric_requests[mt.field_name] = MetricValue(self, mt)
        return self.metric_requests[mt.field_name]

    def __call__(self, *args: List[Dict[str, Any]], **kwargs):
        # print("Call", kwargs)
        mk = self.get_metric_key(**kwargs)
        if mk[1] or mk[2]:
            self.current_metric_key = mk
            if mk not in self.metric_keys:
                self.metric_keys.add(mk)
        return self

    def add_keys(self, keys: List[Dict[str, Any]]):
        for p in keys:
            mk = self.get_metric_key(**p)
            self.metric_keys.add(mk)


class MetricProxy:
    def __init__(self, metric_keys: Optional[List[Dict[str, Any]]] = None):
        self._scopes: Dict[str, "MetricScopeProxy"] = {}
        self._metric_keys = metric_keys

    def __getattr__(self, item) -> "MetricScopeProxy":
        if item in self._scopes:
            return self._scopes[item]
        scope = MetricScope.get_by_table_name(item)
        if not scope:
            raise AttributeError("Unknown scope: %s" % item)
        msp = MetricScopeProxy(scope)
        if self._metric_keys:
            msp.add_keys(self._metric_keys)
        self._scopes[scope.table_name] = msp
        return msp


# Avoid circular references
from noc.sa.models.managedobject import ManagedObject
