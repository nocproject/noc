# ----------------------------------------------------------------------
# Load Metrics DataSource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import time
from typing import Any, AsyncIterable, Dict, List, Optional, Iterable, Tuple

# Third-party modules
import orjson

# NOC modules
from .base import FieldInfo, FieldType, BaseDataSource, ParamInfo
from noc.config import config
from noc.core.clickhouse.connect import connection
from noc.core.datasources.loader import loader as ds_loader
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.inv.models.resourcegroup import ResourceGroup
from noc.sa.models.managedobject import ManagedObject


INTERFACES_QUERY = f"""
  SELECT
    dictGetUInt64('{config.clickhouse.db_dictionaries}.managedobject', 'id', managed_object) as managed_object_id,
    managed_object as managed_object,
    interface as iface_name,
    dictGetString('{config.clickhouse.db_dictionaries}.interfaceattributes', 'profile', (managed_object, interface)) as iface_profile,
    dictGetString('{config.clickhouse.db_dictionaries}.interfaceattributes', 'description', (managed_object, interface)) as iface_description,
    if(max(speed)=0, dictGetUInt64('{config.clickhouse.db_dictionaries}.interfaceattributes', 'in_speed', (managed_object, interface)), max(speed)) as iface_speed,
    round(quantile(0.90)(load_in), 0) as load_in_perc,
    round(avg(load_in), 0) as load_in_avg,
    round(quantile(0.90)(load_in) / if(max(speed)=0, dictGetUInt64('{config.clickhouse.db_dictionaries}.interfaceattributes', 'in_speed', (managed_object, interface)), max(speed)), 4) * 100 as load_in_p,
    round(quantile(0.90)(load_out), 0) as load_out_perc,
    round(avg(load_out), 0) as load_out_avg,
    round(quantile(0.90)(load_out) / if(max(speed)=0, dictGetUInt64('{config.clickhouse.db_dictionaries}.interfaceattributes', 'in_speed', (managed_object, interface)), max(speed)), 4) * 100 as load_out_p,
    round((sum(load_in * time_delta) / 8) / 1048576) as octets_in_sum,
    round((sum(load_out * time_delta) / 8) / 1048576) as octets_out_sum,
    quantile(0.90)(errors_in) as errors_in,
    sum(errors_in_delta) as errors_in_sum,
    quantile(0.90)(errors_out) as errors_out,
    sum(errors_out_delta) as errors_out_sum,
    quantile(0.90)(discards_in) as discards_in,
    quantile(0.90)(discards_out) as discards_out,
    countEqual(arrayMap((a, p) -> a + p, arrayPushFront(groupArray(status_oper), groupArray(status_oper)[1]), arrayPushBack(groupArray(status_oper), groupArray(status_oper)[-1])), 1) as interface_flap,
    anyLast(lastchange) as lastchange,
    anyLast(status_oper) as status_oper_last
  FROM
    noc.interface
  WHERE
    date >= toDate(%d) AND ts >= toDateTime(%d) AND ts <= toDateTime(%d)
    %s %s
  GROUP BY
    managed_object, interface
  %s
  FORMAT JSONEachRow
"""

OBJECTS_QUERY = f"""
  WITH
  tc AS (
    SELECT managed_object as managed_object, avg(usage) as usage
    FROM noc.cpu
    WHERE date >= toDate(%d) AND ts >= toDateTime(%d) AND ts <= toDateTime(%d)
    %s
    GROUP BY managed_object
  ),
  tm AS (
    SELECT managed_object as managed_object, avg(usage) as usage
    FROM noc.memory
    WHERE date >= toDate(%d) AND ts >= toDateTime(%d) AND ts <= toDateTime(%d)
    %s
    GROUP BY managed_object
  )
  SELECT
    dictGetUInt64('{config.clickhouse.db_dictionaries}.managedobject', 'id', tc.managed_object) as managed_object_id,
    tc.managed_object,
    tc.usage as cpu_usage,
    tm.usage as memory_usage
  FROM tc
  LEFT JOIN tm ON tm.managed_object=tc.managed_object
  FORMAT JSONEachRow
"""

PING_QUERY = f"""
  SELECT
    dictGetUInt64('{config.clickhouse.db_dictionaries}.managedobject', 'id', managed_object) as managed_object_id,
    managed_object as managed_object,
    avg(rtt) as ping_rtt,
    max(attempts) as ping_attempts
  FROM
    noc.ping
  WHERE
    date >= toDate(%d) AND ts >= toDateTime(%d) AND ts <= toDateTime(%d)
    %s
  GROUP BY
    managed_object
  FORMAT JSONEachRow
"""

query_map = {
    "load_interfaces": INTERFACES_QUERY,
    "load_cpu": OBJECTS_QUERY,
    "ping": PING_QUERY,
}
CHUNK_SIZE = 5000


class LoadMetricsDS(BaseDataSource):
    name = "loadmetricsds"
    row_index = "managed_object_id"
    fields = [
        FieldInfo(name="managed_object_id", type=FieldType.UINT),
        FieldInfo(name="managed_object_bi_id"),
        # Interfaces
        FieldInfo(name="iface_name"),
        FieldInfo(name="iface_profile"),
        FieldInfo(name="iface_description"),
        FieldInfo(name="iface_speed"),
        FieldInfo(name="load_in_perc", type=FieldType.UINT64),
        FieldInfo(name="load_in_avg", type=FieldType.UINT64),
        FieldInfo(name="load_in_p", type=FieldType.FLOAT),
        FieldInfo(name="load_out_perc", type=FieldType.UINT64),
        FieldInfo(name="load_out_avg", type=FieldType.UINT64),
        FieldInfo(name="load_out_p", type=FieldType.FLOAT),
        FieldInfo(name="octets_in_sum", type=FieldType.UINT64),
        FieldInfo(name="octets_out_sum", type=FieldType.UINT64),
        FieldInfo(name="errors_in", type=FieldType.UINT64),
        FieldInfo(name="errors_in_sum", type=FieldType.UINT64),
        FieldInfo(name="errors_out", type=FieldType.UINT64),
        FieldInfo(name="errors_out_sum", type=FieldType.UINT64),
        FieldInfo(name="discards_in", type=FieldType.UINT),
        FieldInfo(name="discards_out", type=FieldType.UINT),
        FieldInfo(name="interface_flap", type=FieldType.UINT),
        FieldInfo(name="lastchange", type=FieldType.UINT),
        FieldInfo(name="status_oper_last", type=FieldType.UINT),
        FieldInfo(name="interface_load_url"),
        FieldInfo(name="mac_counter"),
        # Objects
        FieldInfo(name="slot"),
        FieldInfo(name="cpu_usage", type=FieldType.FLOAT),
        FieldInfo(name="memory_usage", type=FieldType.FLOAT),
        # Ping
        FieldInfo(name="ping_rtt", type=FieldType.FLOAT),
        FieldInfo(name="ping_attempts", type=FieldType.UINT),
    ]
    params = [
        # reporttype is a choice from "load_interfaces", "load_cpu", "ping"
        ParamInfo(name="reporttype", type="str", required=True),
        ParamInfo(name="start", type="datetime", required=True),
        ParamInfo(name="end", type="datetime", required=True),
        ParamInfo(name="segment", type="str", model="inv.NetworkSegment"),
        # administrative_domain
        ParamInfo(name="resource_group", type="str", model="inv.ResourceGroup"),
        ParamInfo(name="interface_profile", type="str", model="inv.InterfaceProfile"),
        ParamInfo(name="exclude_zero", type="bool", default=False),
    ]

    @staticmethod
    def get_filter(filters: Dict[str, Any]) -> Dict[str, Any]:
        r = {}
        if "resource_group" in filters:
            r["effective_service_groups__overlap"] = ResourceGroup.get_nested_ids(
                filters["resource_group"],
                convert_oid=True,
            )
        if "segment" in filters:
            r["segment__in"] = filters["segment"].get_nested_ids()
        return r

    @classmethod
    async def iter_query(
        cls,
        fields: Optional[Iterable[str]] = None,
        reporttype: str = None,
        start: datetime.datetime = None,
        end: datetime.datetime = None,
        interface_profile: Optional[InterfaceProfile] = None,
        exclude_zero: bool = False,
        admin_domain_ads: Optional[List[int]] = None,
        *args,
        **kwargs,
    ) -> AsyncIterable[Tuple[str, str]]:
        def get_interface_load_url(mo_bi_id):
            path = "/ui/grafana/dashboard/script/report.js"
            params = {
                "title": "interface",
                "biid": mo_bi_id,
                "obj": "blabla",
                "iface": "",
                "from": int(ts_from_date * 1000),
                "to": int(ts_to_date * 1000),
            }
            params_all = "&".join([f"{k}={v}" for k, v in params.items()])
            return f"{path}?{params_all}"

        def value_to_float(v):
            if v is None or isinstance(value, (float, int)):
                return v
            if isinstance(value, str):
                try:
                    return float(v)
                except ValueError:
                    return None

        def value_to_int(v):
            if v is None or isinstance(value, int):
                return v
            if isinstance(value, str):
                try:
                    return int(v)
                except ValueError:
                    return None

        end = end + datetime.timedelta(days=1)
        ts_from_date = time.mktime(start.timetuple())
        ts_to_date = time.mktime(end.timetuple())
        q_filter = cls.get_filter(kwargs)
        q_filter["is_managed"] = True
        mos = ManagedObject.objects.filter(**q_filter)
        if admin_domain_ads:
            mos = mos.filter(administrative_domain__in=admin_domain_ads)
        mo_bi_ids = list(mos.values_list("bi_id", flat=True))
        # Prepare columns list for query in ClickHouse
        ch_columns_map = {
            "load_interfaces": [
                "iface_name",
                "iface_profile",
                "iface_description",
                "iface_speed",
                "load_in_perc",
                "load_in_avg",
                "load_in_p",
                "load_out_perc",
                "load_out_avg",
                "load_out_p",
                "octets_in_sum",
                "octets_out_sum",
                "errors_in",
                "errors_in_sum",
                "errors_out",
                "errors_out_sum",
                "discards_in",
                "discards_out",
                "interface_flap",
                "lastchange",
                "status_oper_last",
            ],
            "load_cpu": ["slot", "cpu_usage", "memory_usage"],
            "ping": ["ping_rtt", "ping_attempts"],
        }
        columns = ch_columns_map[reporttype]
        # Prepare data on the number of MAC-addresses
        mac_counters = {}
        if reporttype == "load_interfaces" and (not fields or "mac_counter" in fields):
            mac_ds = ds_loader["interfacemacsstatds"]
            data = mac_ds.query_sync(resolve_managedobject_id=False, start=start, end=end)
            mac_counters = {
                (r["managed_object_id"], r["interface_name"]): r["mac_count"]
                for r in data.to_dicts()
            }
        # Prepare query from ClickHouse
        query = query_map[reporttype]
        ifp_filter = ""
        if reporttype == "load_interfaces" and interface_profile:
            ifp_filter = f"AND iface_profile='{interface_profile.name}'"
        having_section = ""
        if reporttype == "load_interfaces" and exclude_zero:
            having_section = "HAVING max(load_in) != 0 AND max(load_out) != 0"
        ch_client = connection()
        # Run chunked query and yield data
        num = 1
        ids = mo_bi_ids
        while ids:
            chunk, ids = ids[:CHUNK_SIZE], ids[CHUNK_SIZE:]
            mo_filter = ", ".join(str(id) for id in chunk)
            mo_filter = f"AND managed_object IN ({mo_filter})"
            q_params = [ts_from_date, ts_from_date, ts_to_date, mo_filter]
            if reporttype == "load_interfaces":
                q_params.extend([ifp_filter, having_section])
            elif reporttype == "load_cpu":
                q_params.extend([ts_from_date, ts_from_date, ts_to_date, mo_filter])
            body = ch_client.execute(query % tuple(q_params), return_raw=True)
            for row_b in body.splitlines():
                row = orjson.loads(row_b)  # dict
                mo_bi_id = row["managed_object"]
                yield num, "managed_object_id", int(row["managed_object_id"])
                yield num, "managed_object_bi_id", mo_bi_id
                for c in columns:
                    value = row.get(c)
                    if cls.field_by_name(c).type == FieldType.FLOAT:
                        yield num, c, value_to_float(value)
                    elif cls.field_by_name(c).type in (FieldType.UINT, FieldType.UINT64):
                        yield num, c, value_to_int(value)
                    else:
                        yield num, c, str(row.get(c, ""))
                # Additional fields for 'Interfaces' source
                if reporttype == "load_interfaces" and (
                    not fields or "interface_load_url" in fields
                ):
                    yield num, "interface_load_url", get_interface_load_url(mo_bi_id)
                if reporttype == "load_interfaces" and (not fields or "mac_counter" in fields):
                    yield (
                        num,
                        "mac_counter",
                        mac_counters.get((int(mo_bi_id), row["iface_name"]), ""),
                    )
                num += 1
