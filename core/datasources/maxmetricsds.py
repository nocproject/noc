# ----------------------------------------------------------------------
# Load Metrics max DataSource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict
import datetime
import time
from typing import Any, AsyncIterable, Dict, List, Optional, Iterable, Tuple

# Third-party modules
from pymongo import ReadPreference

# NOC modules
from noc.config import config
from noc.core.clickhouse.connect import connection
from noc.core.mongo.connection import get_db
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.inv.models.resourcegroup import ResourceGroup
from .base import FieldInfo, FieldType, BaseDataSource, ParamInfo

QUERY = f"""SELECT
    managed_object AS mo_bi_id,
    arrayStringConcat(path) AS iface_name,
    dictGetString('{config.clickhouse.db_dictionaries}.interfaceattributes','description' , (managed_object, arrayStringConcat(path))) AS iface_description,
    dictGetString('{config.clickhouse.db_dictionaries}.interfaceattributes', 'profile', (managed_object, arrayStringConcat(path))) AS iface_profile,
    dictGetUInt64('{config.clickhouse.db_dictionaries}.interfaceattributes', 'in_speed', (managed_object, arrayStringConcat(path))) AS iface_speed,
    divide(max(load_in),1048576) AS max_load_in,
    argMax(ts,load_in) AS max_load_in_time,
    divide(max(load_out),1048576) AS max_load_out,
    argMax(ts,load_out) AS max_load_out_time,
    divide(avg(load_in),1048576) AS avg_load_in,
    divide(avg(load_out),1048576) AS avg_load_out
FROM noc.interface
WHERE %s AND date >= toDate(%d) AND ts >= toDateTime(%d) AND ts <= toDateTime(%d)
GROUP BY managed_object, path
HAVING isNotNull(max_load_in) AND isNotNull(max_load_out)
ORDER BY managed_object, path
"""
CHUNK_SIZE = 1000


class MaxMetricsDS(BaseDataSource):
    name = "maxmetricsds"
    row_index = "managed_object_id"
    fields = [
        FieldInfo(name="managed_object_id", type=FieldType.UINT),
        FieldInfo(name="managed_object_bi_id"),
        FieldInfo(name="iface_name"),
        FieldInfo(name="iface_description"),
        FieldInfo(name="iface_profile"),
        FieldInfo(name="iface_speed"),
        FieldInfo(name="max_load_in", type=FieldType.FLOAT),
        FieldInfo(name="max_load_in_time"),
        FieldInfo(name="max_load_out", type=FieldType.FLOAT),
        FieldInfo(name="max_load_out_time"),
        FieldInfo(name="avg_load_in", type=FieldType.FLOAT),
        FieldInfo(name="avg_load_out", type=FieldType.FLOAT),
        FieldInfo(name="total_in", type=FieldType.FLOAT),
        FieldInfo(name="total_out", type=FieldType.FLOAT),
        FieldInfo(name="uplink_iface_name"),
        FieldInfo(name="uplink_iface_description"),
        FieldInfo(name="uplink_iface_profile"),
        FieldInfo(name="uplink_iface_speed"),
        FieldInfo(name="uplink_max_load_in", type=FieldType.FLOAT),
        FieldInfo(name="uplink_max_load_in_time"),
        FieldInfo(name="uplink_max_load_out", type=FieldType.FLOAT),
        FieldInfo(name="uplink_max_load_out_time"),
        FieldInfo(name="uplink_avg_load_in", type=FieldType.FLOAT),
        FieldInfo(name="uplink_avg_load_out", type=FieldType.FLOAT),
        FieldInfo(name="uplink_total_in", type=FieldType.FLOAT),
        FieldInfo(name="uplink_total_out", type=FieldType.FLOAT),
    ]
    params = [
        ParamInfo(name="start", type="datetime", required=True),
        ParamInfo(name="end", type="datetime", required=True),
        ParamInfo(name="segment", type="str", model="inv.NetworkSegment"),
        # administrative_domain
        ParamInfo(name="resource_group", type="str", model="inv.ResourceGroup"),
        ParamInfo(name="mo_profile", type="int", model="sa.ManagedObjectProfile"),
        ParamInfo(name="interface_profile", type="str", model="inv.InterfaceProfile"),
        ParamInfo(name="description", type="str", default=""),
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

    @staticmethod
    def get_links(mos):
        def load(mo_ids):
            data = (
                get_db()["noc.links"]
                .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
                .aggregate(
                    [
                        {"$unwind": "$interfaces"},
                        {
                            "$lookup": {
                                "from": "noc.interfaces",
                                "localField": "interfaces",
                                "foreignField": "_id",
                                "as": "int",
                            }
                        },
                        {"$match": {"int.managed_object": {"$in": mo_ids}}},
                        {
                            "$group": {
                                "_id": "$_id",
                                "links": {
                                    "$push": {
                                        "iface_n": "$int.name",
                                        "mo": "$int.managed_object",
                                        "linked_obj": "$linked_objects",
                                    }
                                },
                            }
                        },
                    ],
                    allowDiskUse=True,
                )
            )
            res = defaultdict(dict)
            for v in data:
                if v["_id"]:
                    for vv in v["links"]:
                        if len(vv["linked_obj"]) == 2:
                            mo = vv["mo"][0]
                            iface = vv["iface_n"]
                            for i in vv["linked_obj"]:
                                if mo != i:
                                    res[mo][i] = iface[0]
            return res

        links = {}
        mos_id = list(mos.values_list("id", flat=True))
        uplinks = {obj: [] for obj in mos_id}
        for mo_id, mo_uplinks in list(mos.values_list("id", "uplinks")):
            uplinks[mo_id] = mo_uplinks or []
        rld = load(mos_id)
        for mo in uplinks:
            for uplink in uplinks[mo]:
                if rld[mo]:
                    if mo in links:
                        links[mo] += [rld[mo][uplink]]
                    else:
                        links[mo] = [rld[mo][uplink]]
        return links

    @classmethod
    async def iter_query(
        cls,
        fields: Optional[Iterable[str]] = None,
        start: datetime.datetime = None,
        end: datetime.datetime = None,
        mo_profile: Optional[ManagedObjectProfile] = None,
        interface_profile: Optional[InterfaceProfile] = None,
        description: Optional[str] = None,
        exclude_zero: bool = False,
        admin_domain_ads: Optional[List[int]] = None,
        *args,
        **kwargs,
    ) -> AsyncIterable[Tuple[str, str]]:
        def str_to_float(str):
            return float("{0:.3f}".format(float(str)))

        end = end + datetime.timedelta(days=1)
        diff = end - start
        q_filter = cls.get_filter(kwargs)
        q_filter["is_managed"] = True
        mos = ManagedObject.objects.filter(**q_filter)
        if admin_domain_ads:
            mos = mos.filter(administrative_domain__in=admin_domain_ads)
        if mo_profile:
            mos = mos.filter(object_profile=mo_profile)
        # Find uplinks
        links = {}
        if not fields or any(f.startswith("uplink") for f in fields):
            links = cls.get_links(mos)
        # Prepare query to ClickHouse
        biid_map = dict(mos.values_list("bi_id", "id"))  # map: MO.bi_id -> MO.id
        mo_bi_ids = tuple(biid_map)
        ch_client = connection()
        ts_start = time.mktime(start.timetuple())
        ts_end = time.mktime(end.timetuple())
        query = QUERY % ("%s", ts_start, ts_start, ts_end)
        # Write metrics data to 3-level dictionary
        # ifaces_metrics[mo_bi_id][iface_name][metric_name] -> value
        ifaces_metrics: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(dict)
        while mo_bi_ids:
            chunk, mo_bi_ids = mo_bi_ids[:CHUNK_SIZE], mo_bi_ids[CHUNK_SIZE:]
            mo_filter = "managed_object IN (%s)" % ", ".join([str(c) for c in chunk])
            for (
                mo_bi_id,
                iface_name,
                iface_description,
                iface_profile,
                iface_speed,
                max_load_in,
                max_load_in_time,
                max_load_out,
                max_load_out_time,
                avg_load_in,
                avg_load_out,
            ) in ch_client.execute(query % mo_filter):
                avg_in = str_to_float(avg_load_in)
                avg_out = str_to_float(avg_load_out)
                total_in = avg_in * diff.total_seconds() / 8
                total_out = avg_out * diff.total_seconds() / 8
                ifaces_metrics[mo_bi_id][iface_name] = {
                    "iface_name": iface_name,
                    "iface_description": iface_description,
                    "iface_profile": iface_profile,
                    "iface_speed": iface_speed,
                    "max_load_in": str_to_float(max_load_in),
                    "max_load_in_time": max_load_in_time,
                    "max_load_out": str_to_float(max_load_out),
                    "max_load_out_time": max_load_out_time,
                    "avg_load_in": avg_in,
                    "avg_load_out": avg_out,
                    "total_in": float("{0:.1f}".format(total_in)),
                    "total_out": float("{0:.1f}".format(total_out)),
                }
        # Yielding data
        num = 1
        for mo_bi_id in ifaces_metrics:
            mo_id = biid_map[int(mo_bi_id)]
            mo_ifaces = set(ifaces_metrics[mo_bi_id])
            for iface in ifaces_metrics[mo_bi_id]:
                if (
                    exclude_zero
                    and ifaces_metrics[mo_bi_id][iface]["max_load_in"] == 0
                    and ifaces_metrics[mo_bi_id][iface]["max_load_out"] == 0
                ):
                    continue
                if (
                    description
                    and description not in ifaces_metrics[mo_bi_id][iface]["iface_description"]
                ):
                    continue
                if (
                    interface_profile
                    and interface_profile.name
                    not in ifaces_metrics[mo_bi_id][iface]["iface_profile"]
                ):
                    continue
                without_uplinks = True
                # Write devices with uplinks
                if mo_id in links:
                    for iface_uplink in links[mo_id]:
                        if iface_uplink in mo_ifaces:
                            yield num, "managed_object_id", mo_id
                            yield num, "managed_object_bi_id", mo_bi_id
                            for k, v in ifaces_metrics[mo_bi_id][iface].items():
                                yield num, k, v
                            for k, v in ifaces_metrics[mo_bi_id][iface_uplink].items():
                                yield num, "uplink_" + k, v
                            num += 1
                            without_uplinks = False
                # Write devices without uplinks
                if without_uplinks:
                    yield num, "managed_object_id", mo_id
                    yield num, "managed_object_bi_id", "-" + mo_bi_id
                    for k, v in ifaces_metrics[mo_bi_id][iface].items():
                        yield num, k, v
                    for k in ifaces_metrics[mo_bi_id][iface]:
                        yield num, "uplink_" + k, None
                    num += 1
