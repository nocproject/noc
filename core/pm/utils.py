# ----------------------------------------------------------------------
# PM Utils
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import itertools
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, Union, Tuple, Dict, Optional, Any, List, Set, FrozenSet, DefaultDict

# Third-party modules
import orjson

# NOC Modules
from noc.pm.models.metricscope import MetricScope
from noc.pm.models.metrictype import MetricType
from noc.pm.models.scale import Scale
from noc.pm.models.measurementunits import MeasurementUnits
from noc.core.clickhouse.connect import connection as ch_connection
from noc.core.clickhouse.error import ClickhouseError


@dataclass(frozen=True)
class Condition:
    field: str
    value: Any
    condition: str = "="
    labels: Optional[List[str]] = None

    def get_expr(self) -> str:
        if self.condition == "in":
            return f"{self.field} IN {tuple(self.value)!r}"
        return f"{self.field} = {self.value}"


@dataclass(frozen=True)
class MetricValue:
    """
    Metric Value class. Return value when call
    Attributes:
        value: Metric Value
        meta: Dict for meta fields
        value_scale: Metric Scale
        value_units: Metric Units
    """

    value: float
    meta: Dict[str, str]
    value_scale: Optional["Scale"] = None
    value_units: Optional["MeasurementUnits"] = None
    value_type: Optional["MetricType"] = None

    def __str__(self):
        # Type, Scale for int value
        if not self.meta:
            return str(self.value)
        meta = [f"{v}" for k, v in self.meta.items() if k != "managed_object"]
        return f"{'@'.join(meta)}: {self.value}"

    def __getattr__(self, item):
        if item in self.meta:
            return self.meta[item]
        raise AttributeError("Unknown Attribute")

    def humanize(self) -> str:
        """Convert metric value to human output"""
        if self.value is None:
            return "-"
        if not self.value_units:
            return "%s %s" % Scale.humanize(int(self.value))
        elif self.value_units.code == "s":
            return Scale.humanize_time(int(self.value))
        return self.value_units.humanize(self.value)

    @property
    def humanize_meta(self) -> str:
        if not self.meta:
            return ""
        return str(self.meta)


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


class QueryField:
    """
    Query Field class, Describe field that append to requested from DB
    """

    function_alias: Dict[str, Function] = {
        "last": Function("argMax", alias="last", args="ts"),
        "count": Function("count", alias="count"),
        "distinct": Function("distinct", alias="distinct"),
        "count_distinct": Function("count", Function("distinct"), alias="count_distinct"),
    }

    def __init__(
        self,
        field: str,
        alias: Optional[str] = None,
        scale: Optional[Scale] = None,
        measure: Optional[MeasurementUnits] = None,
        function: Optional[Union[str, Function]] = None,
        metric_type: Optional[MetricType] = None,
    ):
        self.field: str = field
        if isinstance(function, str):
            self.function = self.function_alias[function]
        else:
            self.function = function or Function("argMax", alias="last", args="ts")
        self.scale: Optional[Scale] = scale
        self.units: Optional[MeasurementUnits] = measure
        self._alias = alias
        self._type = metric_type

    @property
    def query_expr(self) -> str:
        """SQL Expression on query"""
        return self.function.get_expr(self.field)

    @property
    def alias(self) -> str:
        """Field Alias"""
        return self._alias or f"{self.field}_{self.function.alias}"

    @classmethod
    def from_query(
        cls, name: str, alias: Optional[str] = None, table_name: Optional[str] = None
    ) -> "QueryField":
        """
        Build QueryField from query alias
        Attrs:
            name: column name on query
            alias: column alias
        """
        # if "__" in name:
        #    ...
        mt = MetricType.get_by_field_name(name, scope=table_name or None)
        if not mt:
            raise AttributeError("Unknown Field Name: %s" % name)
        return QueryField(
            field=mt.field_name,
            scale=mt.scale,
            measure=mt.units,
            alias=alias,
            metric_type=mt,
        )


class QuerySet:
    """Clickhouse query description"""

    def __init__(
        self,
        proxy: "MetricScopeProxy",
        group_by: Optional[Tuple[str, ...]] = None,
    ):
        """
        # Cached return values
        Attrs:
            proxy: Metric Scope Proxy
            group_by: Group by fields list ?function
        """
        self.metric_proxy: "MetricScopeProxy" = proxy
        self.fields: Dict[str, QueryField] = {}
        self.group_by = group_by or []
        # self.query_cache: Dict[str, List["MetricValue"]] = defaultdict(list)
        self.query_cache: Dict[FrozenSet[Tuple[str, str]], Dict[str, List[MetricValue]]] = {}
        # List Metric Values - series
        self.last_field: Optional[str] = None
        self.include_last_ts: bool = False

    def __str__(self) -> str:
        return f"Query Set Fields: {self.fields.keys()}"

    def __getattr__(self, item) -> "QuerySet":
        self.add_query_field(item, item)
        return self

    def __call__(
        self,
        *args,
        field: Optional[str] = None,
        function: Optional[Union[str, Function]] = None,
        **kwargs,
    ) -> "QuerySet":
        if field:
            self.fields[self.last_field].field = field
        if function:
            self.fields[field or self.last_field].function = function
        return self

    def is_meta_field(self, field: str) -> bool:
        """Check field is meta (name in labels column)"""
        for ll in self.metric_proxy.scope.labels:
            if ll.view_column and ll.view_column == field:
                return True
            if ll.store_column and ll.store_column == field:
                return True
        return False

    def has_field(self, field: str) -> bool:
        if isinstance(field, str):
            return field in self.fields
        elif isinstance(field, QueryField):
            return field.alias in self.fields
        return False

    def query_expr(self) -> str:
        """Build SQL: Expression on query"""
        select = []
        if self.include_last_ts:
            select = ["argMax(ts, ts) as last_ts"]
        group_by = set()
        for g in self.group_by:
            select.append(g)
            group_by.add(g)
        # for c in self.metric_proxy.query_conditions:
        #    select.append(f"argMax({c.field}, ts) AS {c.field}")
        for alias, f in self.fields.items():
            if alias in self.requested_fields:
                # Already Requested
                continue
            select.append(f"{f.query_expr} AS {alias}")
        SQL = """
              SELECT %s
              FROM %s
              WHERE
              date >= %%s
              AND ts >= %%s
              AND (%s)
              %s
              FORMAT JSONEachRow
           """ % (
            ", ".join(select),
            self.metric_proxy.scope.table_name,
            " AND ".join(c.get_expr() for c in self.metric_proxy.query_conditions),
            # " AND hasAny(labels, [%s]) " % ", ".join(labels) if labels else "",
            "GROUP BY %s" % ", ".join(sorted(group_by)) if group_by else "",
        )
        return SQL

    def query_metrics(self):
        """Run build query and fill query_cache result"""
        ch = ch_connection()
        print("Query metrics", self.requested_fields, self.fields.keys())
        # from_date = datetime.datetime.now().replace(microsecond=0) - datetime.timedelta(minutes=30)
        from_date = datetime.datetime.fromisoformat("2024-04-13 18:49:44")
        result = ch.execute(
            sql=self.query_expr(),
            args=[from_date.date().isoformat(), from_date.isoformat(sep=" ")],
            return_raw=True,
        )
        for row in result.splitlines():
            row = orjson.loads(row)
            key = self.get_group_key(row)
            if key not in self.query_cache:
                self.query_cache[key] = defaultdict(list)
            meta = {}
            # group key - group_by fields + key_fields on condition
            for name, value in row.items():
                # Metrics
                if name in self.fields:
                    self.query_cache[key][name].append(
                        MetricValue(
                            float(value) if value else value,
                            meta,
                            value_units=self.fields[name].units,
                            value_scale=self.fields[name].scale,
                            value_type=self.fields[name]._type,
                        )
                    )
                elif name == "labels" and value:
                    meta["labels"] = ",".join(value)
                elif self.is_meta_field(name):
                    # meta
                    meta[name] = value

    @classmethod
    def parse_query(cls, sql: str) -> "QuerySet":
        """Build Queryset by SQL Expression"""

    def add_query_field(self, query: Union[QueryField, str], alias: Optional[str] = None):
        """Add Query field for build request"""
        if isinstance(query, str) and self.is_meta_field(query):
            query = QueryField(field=query)
        elif isinstance(query, str):
            query = QueryField.from_query(
                query, alias=alias or query, table_name=self.metric_proxy.scope.table_name
            )
        # if query.alias not in self.fields:
        print("Add Query Field", query)
        self.fields[query.alias] = query
        self.last_field = query.alias

    def value(self, name: Optional[str] = None, **kwargs) -> Optional[MetricValue]:  # ? params
        """Getting value by field name"""
        name = name or self.last_field
        if name not in self.requested_fields:
            self.query_metrics()
        v = list(self.values(**kwargs))
        if not v:
            return None
        return v[0][name]
        # key = self.get_group_key(kwargs)
        # r = self.query_cache[key][name]
        # return r[0]

    def humanize_value(self, name: Optional[str] = None, **kwargs) -> str:
        r = self.value(name, **kwargs)
        if r:
            return r.humanize()
        return "-"

    # get_group_keys ?, get_values by key: list keys, -> getting values
    def get_group_key(self, keys: Dict[str, str]) -> FrozenSet[Tuple[str, str]]:
        """
        Create group key by query fields:
        * Scope key fields
        * Scope meta fields with group by
        Attrs:
            keys: Keys dict
        """
        r = {}
        for kf in self.metric_proxy.scope.key_fields:
            if kf.field_name in keys:
                r[kf.field_name] = (kf.field_name, int(keys[kf.field_name]))
        for k in self.group_by or []:
            if k in r or k not in keys:
                continue
            if k == "labels":
                r[k] = (k, ",".join(keys[k]))
                continue
            r[k] = (k, keys[k])
        return frozenset(r.values())

    def values(self, **kwargs) -> Iterable[Dict[str, MetricValue]]:
        """Getting requested query fields"""
        # **kwargs = group_key, filter by group_key
        # Other meta field, filter by iterate on for
        # r = []
        # managed_object = x, interface = 'xxx'
        # or if managed_object one, interface = 'xxx', load_in: MV, load_out: MV
        if not self.query_cache:
            self.query_metrics()
        group_key = self.get_group_key(kwargs)
        if group_key in self.query_cache:
            yield {k: v[0] for k, v in self.query_cache[group_key].items()}
            return
        for gk in self.query_cache:
            if group_key.intersection(gk):
                yield {k: v[0] for k, v in self.query_cache[gk].items()}

    def iter_all_values(self, **kwargs):
        """Iterate over all requested metrics"""
        if not self.query_cache:
            self.query_metrics()
        for gk in self.query_cache:
            yield {k: v[0] for k, v in self.query_cache[gk].items()}

    # def values_raw(self, **kwargs) -> List[Dict[str, Any]]:
    #     """"""
    #     if not self.query_cache:
    #         self.query_metrics()

    @property
    def requested_fields(self) -> Set[str]:
        fields = set()
        for r in self.query_cache.values():
            fields |= set(r.keys())
        return fields

    def metric_values(self, field: Optional[str] = None) -> Iterable[MetricValue]:
        """Getting requested metrics"""
        if not self.query_cache or frozenset(
            self.requested_fields.symmetric_difference(self.fields.keys())
        ):
            self.query_metrics()
        field = field or self.last_field
        for r in self.query_cache.values():
            if field in r:
                yield from r[field]
        # for v in self.query_cache[field]:
        #    yield v


class MetricScopeProxy:
    """
    Proxy for request metric from scope. Contains queryset separated grop by
    """

    def __init__(
        self,
        scope: MetricScope,
        query: Optional[str] = None,
    ):
        """
        Multiple QuerySet for different group_by query
        Attrs:
            scope: MetricScope reference
            query: Query to Clickhouse for scope data
        """
        self.scope: MetricScope = scope
        self.query: Optional[str] = query
        self.last_group_by: Optional[Tuple[str, ...]] = None
        self.queries: Dict[Optional[Tuple[str, ...]], QuerySet] = {}
        self.query_conditions: List[Condition] = []

    def add_conditions(self, conditions: Dict[str, Any]):
        """Add query condition"""
        # Key conditions, Meta Conditions, Label condition
        for c in conditions:
            if "__" in c:
                f, op = c.split("__")
            else:
                f, op = c, "="
            self.query_conditions.append(
                Condition(
                    field=f,
                    condition=op,
                    value=conditions[c],
                )
            )

    def add_queryset(self, group_by: Optional[List[str]] = None):
        """
        Add queryset for key by group_by. If not set used default group key
        Attrs:
            group_by: Group by key
        """
        if group_by:
            group_by = tuple(group_by)
        if group_by and group_by not in self.queries:
            self.queries[group_by] = QuerySet(self, group_by=group_by)
        elif group_by in self.queries:
            return self.queries[group_by]
        elif not group_by:
            self.queries[None] = QuerySet(self)
        self.last_group_by = group_by
        return self.queries[group_by]

    def get_queryset(self, group_by: Optional[List[str]] = None) -> Optional[QuerySet]:
        """
        Get queryset by group key
        Attrs:
            group_by: Group by key
        """
        if group_by:
            group_by = tuple(group_by)
        if not self.queries:
            return None
        group_by = group_by or self.last_group_by
        return self.queries.get(group_by)

    def __getattr__(self, item) -> "QuerySet":
        qs = self.get_queryset()
        if not qs:
            qs = self.add_queryset()
        getattr(qs, item)
        return qs

    def __call__(
        self,
        *args,
        queries: Optional[List[Union[str, QueryField]]] = None,
        group_by: Optional[List[str]] = None,
        **kwargs,
    ) -> "QuerySet":
        print("Call Item", queries)
        qs = self.get_queryset(group_by)
        if not qs:
            qs = self.add_queryset(group_by)
        for f in queries or []:
            if not qs.has_field(f):
                qs.add_query_field(f)
        return qs

    def render_template(self, template: str) -> str: ...


class MetricProxy:
    """
    Proxy Metric Requests to MetricScope table.
    Example:
        MetricProxy([("managed_object", 22222222)]).interface.load_in(interface="1/1/1").value()
        MetricProxy([("managed_object", 22222222)]).interface.load_in().values()
        MetricProxy([("managed_object", 22222222)]).interface(group_by=None).interface_sum(field="load_in", function="sum").value
        MetricProxy([("managed_object", 22222222)]).interface.load_in.load_out.values()
        MetricProxy([("managed_object", 22222222, "interface": "1/1/1")]).interface(queries=["load_in", "load_out"]).values()
    """

    def __init__(self, query_ts: Optional[datetime.datetime] = None, **kwargs):
        self._scopes: Dict[str, "MetricScopeProxy"] = {}  # Scope Storage
        self._conditions = kwargs

    def __getattr__(self, item) -> "MetricScopeProxy":
        """
        Getting Metric Scope Proxy for request metrics
        Attrs:
            item: MetricScope Table Name
        """
        if item in self._scopes:
            return self._scopes[item]
        scope = MetricScope.get_by_table_name(item)
        if not scope:
            raise AttributeError("Unknown scope: %s" % item)
        msp = MetricScopeProxy(scope)
        if self._conditions:
            msp.add_conditions(self._conditions)
        self._scopes[scope.table_name] = msp
        return msp

    def fill_all_scopes(self):
        """Request all scopes for object"""
        from noc.sa.models.managedobject import ManagedObject
        from noc.sa.models.managedobjectprofile import ManagedObjectProfile

        object_profiles = set(
            ManagedObject.objects.filter(bi_id=self._conditions["managed_object"])
            .distinct("object_profile")
            .values_list("object_profile", flat=True)
        )
        for op in ManagedObjectProfile.objects.filter(id__in=object_profiles):
            if not op.metrics:
                continue
            for mt in op.metrics:
                mt = MetricType.get_by_id(mt["metric_type"])
                if mt.scope.table_name not in self._scopes:
                    msp = MetricScopeProxy(mt.scope)
                    self._scopes[mt.scope.table_name] = msp
                    if self._conditions:
                        msp.add_conditions(self._conditions)
                msp = self._scopes[mt.scope.table_name]
                if msp.scope.labels:
                    qs = msp.add_queryset(group_by=["managed_object", "labels"])
                else:
                    qs = msp.add_queryset(group_by=["managed_object"])
                qs.add_query_field(
                    QueryField.from_query(mt.field_name, table_name=mt.scope.table_name)
                )

    def iter_object_metrics(self):
        """Iterate over all metrics setting for managed_object"""
        self.fill_all_scopes()
        for proxy in self._scopes.values():
            if proxy.scope.labels:
                yield from proxy(group_by=["managed_object", "labels"]).iter_all_values()
            else:
                yield from proxy(group_by=["managed_object"]).iter_all_values()


def get_objects_metrics(
    managed_objects: Union[Iterable, int]
) -> Tuple[Dict[Any, Dict[str, Dict[str, int]]], Dict[Any, datetime.datetime]]:
    """
    Attrs:
        managed_objects:
    Returns:
        Dictionary ManagedObject -> Path -> MetricName -> value
    """
    from noc.sa.models.managedobjectprofile import ManagedObjectProfile
    from noc.sa.models.managedobject import ManagedObject

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
    Dict[Any, Dict[str, Dict[str, Union[float, int]]]],
    Dict[Any, datetime.datetime],
]:
    """

    Attrs:
        managed_objects: ManagedObject list or bi_id list
        metrics: For customization getting metrics
    Returns:
        Dictionary ManagedObject -> Path -> MetricName -> value
    """
    from noc.sa.models.managedobjectprofile import ManagedObjectProfile
    from noc.sa.models.managedobject import ManagedObject

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
    bi_map: Dict[str, Any] = {str(getattr(mo, "bi_id", mo)): mo for mo in managed_objects}
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
