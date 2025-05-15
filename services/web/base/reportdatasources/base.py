# ----------------------------------------------------------------------
# BaseReportDatasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from dataclasses import dataclass, field
from io import BytesIO, StringIO
from typing import List, Optional, Dict, Iterable, Any, Tuple, Callable, Union
import time
import re
import heapq
import itertools
import logging

# Third-party modules
import orjson
from django.db.models import Q as d_Q

# NOC modules
from noc.aaa.models.user import User
from noc.core.comp import smart_bytes
from noc.sa.models.managedobject import ManagedObject
from .report_objectstat import (
    AttributeIsolator,
    CapabilitiesIsolator,
    StatusIsolator,
    ProblemIsolator,
)

logger = logging.getLogger(__name__)


def iterator_to_stream(iterator):
    """Convert an iterator into a stream (None if the iterator is empty)."""
    try:
        return next(iterator), iterator
    except StopIteration:
        return None


def stream_next(stream):
    """Get (next_value, next_stream) from a stream."""
    val, iterator = stream
    return val, iterator_to_stream(iterator)


def merge(iterators):
    """Make a lazy sorted iterator that merges lazy sorted iterators."""
    streams = [iterator_to_stream(g) for g in [iter(y) for y in iterators]]
    heapq.heapify(streams)
    while streams:
        stream = heapq.heappop(streams)
        if stream is not None:
            val, stream = stream_next(stream)
            heapq.heappush(streams, stream)
            yield val


class BaseReportColumn(object):
    """
    Base report column class.
    Column is dataseries: ((id1: value1), (id2: value2)) - id - index sorted by asc
    """

    MAX_ITERATOR = 800000
    name = None  # ColumnName
    fields = None  # RowFields List
    unknown_value = (None,)  # Fill this if empty value
    builtin_sorted = False  # Column index builtin sorted
    multiple_series = False  # Extract return dict columns dataseries
    # {"Series1_name": dataseries1, "Series2_name": dataseries2}

    def __init__(self, sync_ids=None):
        """

        :param sync_ids:
        """
        self.sync_ids = sync_ids  # Sorted Index list
        self.sync_count = itertools.count()
        self.sync_ids_i = iter(self.sync_ids)
        self._current_id = next(self.sync_ids_i, None)  # Current id
        self._value = None  #
        self._end_series = False  # Tre

    def safe_next(self):
        if next(self.sync_count) > self.MAX_ITERATOR:
            raise StopIteration
        return next(self.sync_ids_i, None)

    def _extract(self):
        """
        Generate list of rows. Each row is a list of fields. ("id1", "row1", "row2", "row3", ...)
        :return:
        """
        prev_id = 0
        if self.multiple_series and self.builtin_sorted:
            # return {STREAM_NAME1: iterator1, ....}
            yield from merge(self.extract())
        elif self.multiple_series and not self.builtin_sorted:
            raise NotImplementedError("Multiple series supported onl with builtin sorted")
        elif not self.builtin_sorted:
            # Unsupported builtin sorted.
            yield from sorted(self.extract())
        else:
            # Supported builtin sorted.
            for v in self.extract():
                if v[0] < prev_id:  # Todo
                    return  # Detect unordered stream
                yield v
                prev_id = v[0]

    def extract(self):
        """
        Generate list of rows. Each row is a list of fields. First value - is id
        :return:
        """
        raise NotImplementedError

    def __iter__(self):
        for row in self._extract():
            if not self._current_id:
                break
            # Row: (row_id, row1, ....)
            row_id, row_value = row[0], row[1:]
            if row_id == self._current_id:
                # @todo Check Duplicate ID
                # If row_id equal current sync_id - set value
                self._value = row_value
            elif row_id < self._current_id:
                # row_id less than sync_id, go to next row
                continue
            elif row_id > self._current_id:
                # row_id more than sync_id, go to next sync_id
                while self._current_id and row_id > self._current_id:
                    # fill row unknown_value
                    yield self.unknown_value
                    self._current_id = self.safe_next()
                if row_id == self._current_id:
                    # Match sync_id and row_id = set value
                    self._value = row_value
                else:
                    # Step over current sync_id, set unknown_value
                    # self._value = self.unknown_value
                    continue
            yield self._value  # return current value
            self._current_id = self.safe_next()  # Next sync_id
        self._end_series = True
        # @todo Variant:
        # 1. if sync_ids use to filter in _extract - sync_ids and _extract ending together
        # 2. if sync_ids end before _extract ?
        # 3. if _extract end before sync_ids ?
        if self._current_id:
            # If _extract end before sync_ids to one element
            yield self.unknown_value
        for _ in self.sync_ids_i:
            yield self.unknown_value

    def get_dictionary(self, filter_unknown=False):
        """
        return Dictionary id: value
        :return:
        """
        r = {}
        if not self._current_id:
            return r
        for _ in self:
            if filter_unknown and _[0] is self.unknown_value:
                continue
            r[self._current_id] = _[0]
            if self._end_series:
                break
        return r

    def __getitem__(self, item):
        # @todo use column as dict
        if item == self._current_id:
            return self._value
        return self.unknown_value
        # raise NotImplementedError


class LongestIter(object):
    """
    c_did = DiscoveryID._get_collection()
    did = c_did.find({"hostname": {"$exists": 1}},
    {"object": 1, "hostname": 1}).sort("object")
        # did = DiscoveryID.objects.filter(hostname__exists=True
        ).order_by("object").scalar("object", "hostname").no_cache()
    hostname = LongestIter(did)
    """

    def __init__(self, it):
        self._iterator = it
        self._end_iterator = False
        self._id = 0
        self._value = None
        self._default_value = None

    def __getitem__(self, item):
        if self._end_iterator:
            return self._default_value
        if self._id == item:
            return self._value
        elif self._id < item:
            self._id = item
            next(self, None)
            return self._value
        elif self._id > item:
            # print("Overhead")
            pass
        return self._default_value

    def __iter__(self):
        for val in self._iterator:
            if val["object"] == self._id:
                self._value = val["hostname"]
            elif val["object"] < self._id:
                continue
            elif val["object"] > self._id:
                self._id = val["object"]
                self._value = val["hostname"]
            yield
        self._end_iterator = True


class ReportModelFilter(object):
    """
    Getting statictics info for ManagedObject
    """

    decode_re = re.compile(r"(\d+)(\S+)(\d+)")

    model = ManagedObject  # Set on base class

    def __init__(self):
        self.formulas = """2is1.3hs0, 2is1.3hs0.5is1, 2is1.3hs0.5is2,
                2is1.3hs0.5is2.4hs0, 2is1.3hs0.5is2.4hs1, 2is1.3hs0.5is2.4hs1.5hs1"""
        self.f_map = {
            "is": StatusIsolator(),
            "hs": CapabilitiesIsolator(),
            "a": AttributeIsolator(),
            "isp": ProblemIsolator(),
        }
        self.logger = logger

    def decode(self, formula):
        """
        Decode stat formula and return isolated set
        :param formula:
        :return: moss: Result Query for Object
        :return: ids: Result id list for object
        """
        ids = []
        moss = self.model.objects.filter()
        for f in formula.split("."):
            self.logger.debug("Decoding: %s" % f)
            f_num, f_type, f_val = self.decode_re.findall(f.lower())[0]
            func_stat = self.f_map[f_type]
            func_stat = getattr(func_stat, "get_stat")(f_num, f_val)
            if isinstance(func_stat, set):
                ids += [func_stat]
            # @todo remove d_Q, example changing to class
            elif isinstance(func_stat, d_Q):
                moss = moss.filter(func_stat)
        self.logger.debug(moss.query)
        return moss, ids

    def proccessed(self, column):
        """
        Intersect set for result
        :param column: comma separated string stat formula.
        Every next - intersection prev
        :return:
        """
        r = {}
        for c in column.split(","):
            # print("Next column: %s" % c)
            moss, idss = self.decode(c.strip())
            ids = set(moss.values_list("id", flat=True))
            for i_set in idss:
                ids = ids.intersection(i_set)
            r[c.strip()] = ids.copy()
        return r


@dataclass
class ReportField:
    name: str
    label: str
    description: Optional[str] = ""
    unit: Optional[str] = None
    summary: Optional[bool] = False
    default: Optional[str] = None
    metric_name: Optional[str] = None  # Field name on clickhouse
    group: bool = False
    hidden: bool = False


@dataclass
class FilterValues:
    value: Any
    description: str


@dataclass
class ReportFilter:
    name: str
    type: str
    description: str
    values: Optional[FilterValues]
    required: bool


@dataclass
class ReportConfig:
    name: str
    description: str
    timebased: bool
    enabled: bool
    fields: List[ReportField]
    columns: List[ReportField] = field(init=False)
    groupby: List[str]
    intervals: List[str]
    filters: List[ReportFilter]
    dataretentiondays: int

    def __post_init__(self):
        self.columns = [f for f in self.fields]


class ReportDataSource(object):
    name = None
    description = None
    object_model = None

    # (List#, Name, Alias): TypeNormalizer or (TypeNormalizer, DefaultValue)
    FIELDS: List[ReportField] = []
    INTERVALS: List[str] = ["HOUR"]
    TIMEBASED: bool = False
    SORTED: bool = True

    def __init__(
        self,
        fields: List[str],
        objectids: List[str] = None,
        allobjectids: bool = False,
        start: Optional[datetime.datetime] = None,
        end: Optional[datetime.datetime] = None,
        interval: Optional[str] = None,
        max_intervals: Optional[int] = None,
        filters: Optional[List[Dict[str, Union[List[str], str]]]] = None,
        rows: Optional[int] = None,
        groups: Optional[List[str]] = None,
        user: Optional["User"] = None,
    ):
        self.query_fields: List[str] = fields
        self.fields: Dict[str, ReportField] = self.get_fields(fields)  # OrderedDict
        self.fields_summary = self.get_summary_fields(fields)
        self.objectids = objectids
        self.allobjectids: bool = allobjectids
        self.filters: List[Dict[str, Union[List[str], str]]] = filters or []
        self.interval: str = interval
        self.max_intervals: int = max_intervals
        self.rows: int = rows
        self.groups: List[str] = groups or []
        if self.TIMEBASED and not start:
            raise ValueError("Timebased Report required start param")
        self.end: datetime.datetime = end or datetime.datetime.now()
        self.end = self.end.replace(tzinfo=None)
        self.start: datetime.datetime = start or self.end - datetime.timedelta(days=1)
        self.start = self.start.replace(tzinfo=None)
        self.user = user
        if self.start and self.end and self.start >= self.end:
            raise ValueError("End query timestamp must be more Start")

    @classmethod
    def get_config(cls) -> ReportConfig:
        """
        Return ReportConfig
        :return:
        """
        return ReportConfig(
            name=cls.name,
            description=cls.description,
            timebased=cls.TIMEBASED,
            enabled=True,
            fields=cls.FIELDS,
            groupby=[f.name for f in cls.FIELDS if f.group],
            intervals=cls.INTERVALS,
            filters=[],
            dataretentiondays=1,
        )

    @classmethod
    def get_fields(cls, fields):
        r = {}
        for query_f in fields:
            for f in cls.FIELDS:
                if f.name == query_f and not f.summary:
                    r[query_f] = f
        return r

    @classmethod
    def get_summary_fields(cls, fields):
        r = {}
        for query_f in fields:
            for f in cls.FIELDS:
                if f.name == query_f and f.summary:
                    r[query_f] = f
        return r

    def get_summary_statistics(self) -> Dict[str, Any]:
        # Return summary
        return {}

    def iter_data(self):
        pass

    def extract(self) -> Iterable[Dict[str, int]]:
        """
        Generate list of rows. Each row is a list of fields. First value - is id
        :return:
        """
        raise NotImplementedError

    def report_json(self, fmt: Optional[Callable] = None):
        import orjson

        return orjson.dumps([row for row in self.extract()])

    def report_csv(self, fmt: Optional[Callable] = None) -> bytes:
        import csv

        response = StringIO()
        writer = csv.writer(
            response, dialect="excel", delimiter=";", quotechar='"', quoting=csv.QUOTE_NONNUMERIC
        )
        # Header
        writer.writerow((self.fields[f].label for f in self.fields if not self.fields[f].hidden))
        for row in self.extract():
            writer.writerow((row[f] for f in self.fields if not self.fields[f].hidden))

        return smart_bytes(response.getvalue())

    def report_xlsx(self, fmt: Optional[Callable] = None) -> bytes:
        import xlsxwriter

        response = BytesIO()
        wb = xlsxwriter.Workbook(response)
        cf1 = wb.add_format({"bottom": 1, "left": 1, "right": 1, "top": 1})
        ws = wb.add_worksheet("Data")
        max_column_data_length: Dict[str, int] = {}
        # Header
        for cn, c in enumerate(self.fields):
            if self.fields[c].hidden:
                continue
            label = self.fields[c].label
            if c not in max_column_data_length or len(str(label)) > max_column_data_length[c]:
                max_column_data_length[c] = len(str(label))
            ws.write(0, cn, label, cf1)
        rn, cn = 1, 0
        for rn, row in enumerate(self.extract(), start=1):
            for cn, c in enumerate(self.fields):
                if self.fields[c].hidden:
                    continue
                if c not in max_column_data_length or len(str(row[c])) > max_column_data_length[c]:
                    max_column_data_length[c] = len(str(row[c]))
                ws.write(rn, cn, row[c], cf1)
        # for
        ws.autofilter(0, 0, rn, cn)
        ws.freeze_panes(1, 0)
        for cn, c in enumerate(self.fields):
            # Set column width
            if self.fields[c].hidden:
                continue
            width = 15
            if width < max_column_data_length[c]:
                width = max_column_data_length[c]
            ws.set_column(cn, cn, width=width)
        wb.close()
        response.seek(0)
        return response.getvalue()

    def report(self, report_fmt: str):
        if not hasattr(self, f"report_{report_fmt}"):
            raise NotImplementedError(f"Not supported format {report_fmt}")
        return getattr(self, f"report_{report_fmt}")()


class CHTableReportDataSource(ReportDataSource):
    CHUNK_SIZE = 5000
    TABLE_NAME = None
    object_field = "managed_object"
    ts_field = "ts"

    def get_client(self):
        if not hasattr(self, "_client"):
            from noc.core.clickhouse.connect import connection

            self._client = connection()
        return self._client

    def get_table(self):
        return self.TABLE_NAME

    def get_object_filter(self, ids) -> str:
        return f'{self.object_field} IN ({", ".join([str(c) for c in ids])})'

    group_intervals = {
        "HOUR": "toStartOfHour(toDateTime(ts))",
        "DAY": "toStartOfDay(toDateTime(ts))",
        "WEEK": "toStartOfWeek(toDateTime(ts))",
        "MONTH": "toMonth(toDateTime(ts))",
    }

    def get_group(self) -> Tuple[List[str], List[str]]:
        """
        If set max_intervals - use variants interval
        :return:
        """
        select, group = [], []
        if self.max_intervals:
            minutes = max(((self.end - self.start).total_seconds() / 60) / self.max_intervals, 1)
            select += [f"toStartOfInterval(ts, INTERVAL {minutes} minute) AS ts"]
            group += ["ts"]
        elif self.interval and self.interval not in self.group_intervals:
            raise NotImplementedError("Not supported interval")
        elif self.interval in self.group_intervals:
            select += [f"{self.group_intervals[self.interval]} as ts"]
            group += ["ts"]

        return select, group

    def get_custom_conditions(self) -> Dict[str, List[str]]:
        if not self.filters:
            return {}
        where, having = [], []
        for ff in self.filters:
            f_name = ff["name"]
            for s in self.FIELDS:
                if s.name == f_name:
                    f_name = s.metric_name
                    break
            op = ff.get("op", "IN")
            if op == "IN":
                f_value = f'{tuple(ff["value"])}'
            else:
                f_value = ff["value"][0]
            q = f"{f_name} {op} {f_value}"
            if ff["name"] in self.fields and self.fields[ff["name"]].group:
                where += [q]
            else:
                having += [q]
        return {
            "q_where": where,
            "q_having": having,
        }

    def get_query_ch(
        self, from_date: datetime.datetime, to_date: datetime.datetime, r_format: str = None
    ) -> str:
        ts_from_date = time.mktime(from_date.timetuple())
        ts_to_date = time.mktime(to_date.timetuple())
        select, group = self.get_group()
        query_map = {
            "q_select": select or [],
            "q_group": group or [],
            "q_where": [
                f"(date >= toDate({ts_from_date})) AND ({self.ts_field} >= toDateTime({ts_from_date}) AND {self.ts_field} <= toDateTime({ts_to_date})) %s",  # objectids_filter
            ],
        }

        for ff in self.fields:
            fc = self.fields[ff]
            if fc.group and fc.name in self.groups:
                # query_map["q_select"] += [f"{f.metric_name} as {f.name}"]
                query_map["q_group"] += [f"{fc.metric_name}"]
            query_map["q_select"] += [f"{fc.metric_name} as {fc.name}"]
        if self.interval:
            query_map["q_order_by"] = ["ts"]
        custom_conditions = self.get_custom_conditions()
        if "q_where" in custom_conditions:
            query_map["q_where"] += custom_conditions["q_where"]
        if "q_having" in custom_conditions:
            query_map["q_having"] = custom_conditions["q_having"]
        query = [
            f'SELECT {",".join(query_map["q_select"])}',
            f"FROM {self.get_table()}",
            f'WHERE {" AND ".join(query_map["q_where"])}',
        ]
        if "q_group" in query_map and query_map["q_group"]:
            query += [f'GROUP BY {",".join(query_map["q_group"])}']
        if "q_having" in query_map and query_map["q_having"]:
            query += [f'HAVING {" AND ".join(query_map["q_having"])}']
        if "q_order_by" in query_map:
            query += [f'ORDER BY {",".join(query_map["q_order_by"])}']
        if self.rows:
            query += [f"LIMIT {self.rows}"]
        if r_format:
            query += [f" FORMAT {r_format}"]
        return "\n ".join(query)

    def do_query(self):
        f_date, to_date = self.start, self.end
        query = self.get_query_ch(f_date, to_date, r_format="JSONEachRow")
        logger.info("Query: %s", query)
        client = self.get_client()
        if self.allobjectids or not self.objectids:
            body = client.execute(query % "", return_raw=True)
            for row in body.splitlines():
                yield orjson.loads(row)
        else:
            # chunked query
            ids = self.objectids
            while ids:
                chunk, ids = ids[: self.CHUNK_SIZE], ids[self.CHUNK_SIZE :]
                body = client.execute(
                    query % f" AND {self.get_object_filter(chunk)}", return_raw=True
                )
                for row in body.splitlines():
                    yield orjson.loads(row)

    def extract(self):
        for row in self.do_query():
            yield row
