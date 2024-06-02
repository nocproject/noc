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
from dataclasses import dataclass
import itertools

# Third-party modules
import orjson

# NOC modules
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.core.clickhouse.connect import connection as ch_connection
from noc.core.clickhouse.error import ClickhouseError
from noc.pm.models.metricscope import MetricScope
from noc.pm.models.metrictype import MetricType
from noc.pm.models.measurementunits import MeasurementUnits
from noc.pm.models.scale import Scale


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


MetricKey = Tuple[Tuple[Tuple[str, Any], ...], Tuple[str, ...]]


@dataclass
class Function:
    """
    Aggregate function class
    """

    name: str
    function: Optional["Function"] = None
    alias: Optional[str] = None
    args: Optional[str] = None

    def get_expr(self, field: str):
        if self.function:
            return f"{self.name}({self.function.get_expr(field)})"
        if self.args:
            return f"{self.name}({field}, {self.args})"
        return f"{self.name}({field})"


@dataclass(frozen=True)
class MetricValue:
    """
    Metric Value class. Return value when call
    # def humanize
    """

    value: float
    meta: Dict[str, str]
    value_scale: Optional["Scale"] = None
    value_units: Optional["MeasurementUnits"] = None

    def __str__(self):
        # Type, Scale for int value
        if not self.meta:
            return str(self.value)
        meta = [f"{v}" for k, v in self.meta.items() if k != "managed_object"]
        return f"{'@'.join(meta)}: {self.value}"

    def __hash__(self):
        return hash(self.meta)

    def __eq__(self, other):
        if self.meta == other.meta:
            return True
        return False

    def __getattr__(self, item):
        if item in self.meta:
            return self.meta[item]
        raise AttributeError("Unknown Attribute")


class QueryField:
    """
    Query Field class, Describe field that append to requested from DB
    """

    function_map: Dict[str, Function] = {
        "last": Function("argMax", alias="last", args="ts"),
        "count": Function("count", alias="count"),
        "distinct": Function("distinct", alias="distinct"),
        "count_distinct": Function("count", Function("distinct"), alias="count_distinct"),
    }

    def __init__(
        self,
        proxy: "MetricScopeProxy",
        field: str,
        scale: Optional[Scale] = None,
        measure: Optional[MeasurementUnits] = None,
    ):
        self.metric_proxy = proxy
        self.field: str = field
        self.function: Function = self.function_map["last"]
        self.group_by: Optional[List[str]] = None
        self.scale: Optional[Scale] = scale
        self.units: Optional[MeasurementUnits] = measure

    def __hash__(self):
        return hash(self.function.get_expr(self.field))

    def __str__(self):
        """
        Format requested Metrics
        """
        r = self.values()
        return "<br/>".join(str(x) for x in r)

    @property
    def query_expr(self) -> str:
        """
        Field Expression on query
        """
        return self.function.get_expr(self.field)

    @property
    def alias(self) -> str:
        """
        Field Alias
        """
        return f"{self.field}_{self.function.alias}"

    @property
    def group_key(self) -> Tuple[str, ...]:
        if not self.group_by:
            return tuple()
        return tuple(self.group_by)

    def __getattr__(self, item) -> "QueryField":
        """
        humanize - return str value
        """
        if item in self.function_map:
            self.function = self.function_map[item]
        return self

    def __call__(self, *args, **kwargs) -> "QueryField":  # MetricValue
        """
        scale = convert value by scale
        """
        if "group_by" in kwargs:
            self.group_by = kwargs["group_by"]
        return self

    def values(self, **kwargs) -> List["MetricValue"]:
        return self.metric_proxy.query_metrics([self])


class MetricScopeProxy:
    """
    Proxy Metric Scale

    # Call for multiple fields (cpu_load, cpu_usage).multi
    # metric.cpu.load_in.load_out.sum
    """

    def __init__(self, scope: Optional["MetricScope"] = None):
        self.scope: "MetricScope" = scope
        self.queries: Dict[str, QueryField] = {}  # Requested Queries to MetricScope
        self.query_conditions: Set[MetricKey] = set()  # Predefined conditions to query
        self.query_cache: Dict[QueryField, Dict[MetricKey, List["MetricValue"]]] = (
            {}
        )  # Cached return values

    def get_metric_key(self, fields: Set[str] = None, **kwargs) -> "MetricKey":
        """
        Getting requested MetricKey. Contains Key Field and Key Label. Unique for Metric Instances
        :param fields:
        :param kwargs: Map - KeyFieldName -> KeyFieldValue
        """
        keys = []
        for k in self.scope.key_fields:
            if k.field_name in kwargs:
                # Resolve object if f.field_name__ in kwargs
                keys.append((k.field_name, int(kwargs[k.field_name])))
        for ll in self.scope.labels:
            if ll.store_column in kwargs:
                f = ll.store_column
            elif ll.view_column in kwargs:
                f = ll.view_column
            elif ll.field_name in kwargs:
                f = ll.field_name
            else:
                continue
            if fields and f in fields:
                continue
            keys.append((f, f"{str(kwargs[f])}"))
        if "labels" in kwargs:
            labels = tuple(kwargs["labels"])
        else:
            labels = tuple([])
        return tuple(keys), labels

    def get_query(
        self,
        req_metrics: List[QueryField],
        req_conditions: Set[MetricKey],
        **kwargs,
    ) -> Iterable[str]:
        """
        Build Clickhouse Query by QueryField
        """
        # fields: Set[str] = set()
        group: Dict[Tuple[str, ...], List[QueryField]] = defaultdict(list)
        conditions = defaultdict(list)
        select_fields = set()
        # Processed query group by
        for q in req_metrics:
            # fields.add(q.field)
            group[q.group_key].append(q)
        # Processed query conditions (where)
        for mk in req_conditions:
            key, values = [], []
            # Keys field
            for field, value in mk[0]:
                key.append(field)
                select_fields.add(field)
                values.append(str(value))
            # @todo labels
            conditions[tuple(key)].append("(%s)" % ", ".join(values))
        # Build Final Query select and other
        for g, fields in group.items():
            select, group_by, condition = list(select_fields), list(select_fields), []
            # Select
            for qf in fields:
                select.append(f"{qf.query_expr} AS {qf.alias}")
            # Where
            condition = [
                " (%s) IN (%s)" % (", ".join(cond), ", ".join(values))
                for cond, values in conditions.items()
            ]
            # Group By
            if g:
                select += list(g)
                group_by += list(g)
            SQL = """
                  SELECT argMax(ts, ts), %s
                  FROM %s
                  WHERE
                  date >= %%s
                  AND ts >= %%s
                  AND (%s)
                  %s
                  FORMAT JSONEachRow
               """ % (
                ", ".join(select),
                self.scope.table_name,
                " OR ".join(condition),
                "GROUP BY %s" % ", ".join(group_by) if group_by else "",
            )
            yield SQL

    def query_metrics(self, req_metrics: List[QueryField], **kwargs) -> List["MetricValue"]:
        """
        Gettinig metrics from database
        :param req_metrics: List QueryField for requst
        :param kwargs: Key fields map
        """
        # Build requested MetricKey for condition
        if kwargs:
            mk = self.get_metric_key(**kwargs)
        elif self.current_metric_key:
            mk = self.current_metric_key
        else:
            raise ValueError("Not selected Object for request metrics")
        r: List[MetricValue] = []
        query_map = {}
        query_conditions = set()
        # Proecessed requested metrics for cache check.
        for qf in req_metrics:
            # Get chache
            if qf not in self.query_cache:
                self.query_cache[qf] = defaultdict(list)
                for q in self.query_conditions:
                    query_conditions.add(q)
                    self.query_cache[qf][q] = []
            elif mk in self.query_cache[qf]:
                r += self.query_cache[qf][mk]
                continue
            elif mk not in self.query_cache[qf]:
                self.query_cache[qf][mk] = []
                query_conditions.add(mk)
            # elif qf in self.query_cache and mk in self.query_conditions:
            #     # Nothinп metric on DB for mk
            #     print("Nothinп metric on DB for mk")
            #     continue
            query_map[qf.alias] = qf
        if not query_map:
            return r
        ch = ch_connection()
        # @todo Custom requested interval by DiscoveryInterval
        from_date = datetime.datetime.now().replace(microsecond=0) - datetime.timedelta(minutes=30)
        for query in self.get_query(list(query_map.values()), query_conditions, **kwargs):
            print(query)
            result = ch.execute(
                sql=query,
                args=[from_date.date().isoformat(), from_date.isoformat(sep=" ")],
                return_raw=True,
            )
            for row in result.splitlines():
                row = orjson.loads(row)
                for name, value in row.items():
                    if name not in query_map:
                        continue
                    q = query_map[name]
                    mk = self.get_metric_key(**row)
                    mv = MetricValue(value, dict(mk[0]), value_scale=q.scale, value_units=q.units)
                    # Exclude group by for cached values
                    cache_key = self.get_metric_key(fields=set(q.group_key), **row)
                    if not self.current_metric_key or self.current_metric_key == cache_key:
                        r.append(mv)
                    # Append to Cache
                    if q not in self.query_cache:
                        self.query_cache[q] = defaultdict(list)
                    if mv not in self.query_cache[q][mk]:
                        self.query_cache[q][cache_key] += [mv]
        return r

    def add_keys(self, keys: List[Dict[str, Any]]):
        """
        Add predefined metric Key for query
        """
        for p in keys:
            mk = self.get_metric_key(**p)
            self.query_conditions.add(mk)

    def has_field(self, name: str) -> bool:
        """
        Check field exists on scope
        :param name: Field name
        """
        for label in self.scope.labels:
            if label.store_column == name or label.view_column == name:
                return True
        return False

    def __getattr__(self, item) -> Union["QueryField", "MetricScopeProxy"]:
        # print("ProxyX", item)
        if self.scope and self.scope.table_name == item:
            return self
        elif not self.scope:
            self.scope = MetricScope.get_by_table_name(item)
            return self
        mt = MetricType.get_by_field_name(item, scope=self.scope.table_name)
        if mt:
            qf = QueryField(self, mt.field_name, mt.scale, mt.measure)
        elif self.has_field(item):
            qf = QueryField(self, item)
        else:
            raise AttributeError("[%s] Unknown metric: %s" % (self.scope.name, item))
        if qf.alias in self.queries:
            return self.queries[qf.alias]
        self.queries[qf.alias] = qf
        return qf

    def __call__(self, *args: List[Dict[str, Any]], **kwargs):
        # print("Call", kwargs)
        mk = self.get_metric_key(**kwargs)
        if mk[0] or mk[1]:
            self.current_metric_key = mk
            if mk not in self.query_conditions:
                self.query_conditions.add(mk)
        return self


class MetricProxy:
    """
    Proxy Metic Requests to MetricScope table.
    """

    def __init__(self, metric_keys: Optional[List[Dict[str, Any]]] = None):
        self._scopes: Dict[str, "MetricScopeProxy"] = {}  # Scope Storage
        self._metric_keys = metric_keys  # Predefined Request Keys

    def __getattr__(self, item) -> "MetricScopeProxy":
        """
        Getting Metric Scope Proxy for request metrics
        :param item: MetricScope Table Name
        """
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
