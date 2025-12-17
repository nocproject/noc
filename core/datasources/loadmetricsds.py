# ----------------------------------------------------------------------
# Load Metrics DataSource
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
from noc.services.web.base.reportdatasources.loader import loader


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
        FieldInfo(name="load_in_perc"),
        FieldInfo(name="load_in_avg"),
        FieldInfo(name="load_in_p"),
        FieldInfo(name="load_out_perc"),
        FieldInfo(name="load_out_avg"),
        FieldInfo(name="load_out_p"),
        FieldInfo(name="octets_in_sum"),
        FieldInfo(name="octets_out_sum"),
        FieldInfo(name="errors_in"),
        FieldInfo(name="errors_in_sum"),
        FieldInfo(name="errors_out"),
        FieldInfo(name="errors_out_sum"),
        FieldInfo(name="discards_in"),
        FieldInfo(name="discards_out"),
        FieldInfo(name="interface_flap"),
        # interface_load_url
        FieldInfo(name="lastchange"),
        FieldInfo(name="status_oper_last"),
        # mac_counter
        # Objects
        FieldInfo(name="slot"),
        FieldInfo(name="cpu_usage", type=FieldType.FLOAT),
        FieldInfo(name="memory_usage", type=FieldType.UINT),
        # Ping
        FieldInfo(name="ping_rtt", type=FieldType.FLOAT),
        FieldInfo(name="ping_attempts", type=FieldType.UINT),
    ]
    params = [
        ParamInfo(name="reporttype", type="str", required=True),
        ParamInfo(name="start", type="datetime", required=True),
        ParamInfo(name="end", type="datetime", required=True),
        ParamInfo(name="segment", type="str", model="inv.NetworkSegment"),
        # administrative_domain
        ParamInfo(name="resource_group", type="str", model="inv.ResourceGroup"),
        ParamInfo(name="interface_profile", type="str", model="inv.InterfaceProfile"),
        ParamInfo(name="exclude_zero", type="bool", default=False),
        #ParamInfo(name="exclude_zero", type="bool", default=False),
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
        #exclude_zero: bool = False,
        admin_domain_ads: Optional[List[int]] = None,
        *args,
        **kwargs,
    ) -> AsyncIterable[Tuple[str, str]]:
        end = end + datetime.timedelta(days=1)
        ts_from_date = time.mktime(start.timetuple())
        ts_to_date = time.mktime(end.timetuple())

        q_filter = cls.get_filter(kwargs)
        q_filter["is_managed"] = True
        mos = ManagedObject.objects.filter(**q_filter)
        if admin_domain_ads:
            mos = mos.filter(administrative_domain__in=admin_domain_ads)

        mo_bi_ids = list(mos.values_list("bi_id", flat=True))

        columns_map = {
            "load_interfaces": [
                "iface_name",
                "interface_profile",
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
                #"discards_in_sum",
                "discards_out",
                #"discards_out_sum",
                "interface_flap",
                #
                "lastchange",
                "status_oper_last",
                #
            ],
            "load_cpu": ["slot", "cpu_usage", "memory_usage"],
            "ping": ["ping_rtt", "ping_attempts"],
        }

        report_map = {
            "load_interfaces": {
                "url": "%(path)s?title=interface&biid=%(biid)s"
                       "&obj=%(oname)s&iface=%(iname)s&from=%(from)s&to=%(to)s",
                "datasource": "reportinterfacemetrics",
                "aggregated_source": "reportinterfacemetricsagg",
            },
            "load_cpu": {
                "url": """%(path)s?title=cpu&biid=%(biid)s&obj=%(oname)s&from=%(from)s&to=%(to)s""",
                "datasource": "reportobjectmetrics",
            },
            "ping": {
                "url": """%(path)s?title=ping&biid=%(biid)s&obj=%(oname)s&from=%(from)s&to=%(to)s""",
                "datasource": "reportavailability",
            },
        }
        map_table = {
            "load_interfaces": r"/Interface\s\|\sLoad\s\|\s[In|Out]/",
            "load_cpu": r"/[CPU|Memory]\s\|\sUsage/",
            "errors": r"/Interface\s\|\s[Errors|Discards]\s\|\s[In|Out]/",
            "ping": r"/Ping\s\|\sRTT/",
        }
        d_url = {
            "path": "/ui/grafana/dashboard/script/report.js",
            "rname": map_table[reporttype],
            "from": str(int(ts_from_date * 1000)),
            "to": str(int(ts_to_date * 1000)),
            "biid": "",
            "oname": "",
            "iname": "",
        }

        url = report_map[reporttype]["url"]
        columns = columns_map[reporttype]
        datasource = report_map[reporttype]["datasource"]
        print("-- reporttype", reporttype, type(reporttype))
        print("-- datasource", datasource, type(datasource))
        report = loader[datasource]



        fields = ["managed_object"]
        group = ["managed_object"]
        if reporttype == "load_interfaces":
            fields += ["iface_name"]
            group += ["iface_name"]


        for c in columns:
            fields += [c]

        filters = []
        # mac_counters = {}

        # if reporttype == "load_interfaces" and interface_profile:
        #     interface_profile = InterfaceProfile.objects.filter(id=interface_profile).first()
        #     filters += [{"name": "interface_profile", "value": [interface_profile.name]}]
        # if reporttype == "load_interfaces" and not use_aggregated_source and exclude_zero:
        #     # Op - operand (function) - default IN
        #     filters += [
        #         {"name": "max(load_in)", "value": [0], "op": "!="},
        #         {"name": "max(load_out)", "value": [0], "op": "!="},
        #     ]
        # elif reporttype == "load_interfaces" and use_aggregated_source and exclude_zero:
        #     filters += [
        #         {"name": "maxMerge(load_in_max)", "value": [0], "op": "!="},
        #         {"name": "maxMerge(load_out_max)", "value": [0], "op": "!="},
        #     ]

        data = report(
            fields=fields,
            allobjectids=False,
            objectids=mo_bi_ids,
            start=start,
            end=end,
            groups=group,
            filters=filters,
        )

        # Yielding data
        num = 1
        for row in data.extract():
            # if "interface_load_url" in fields:
            #     d_url["biid"] = row["managed_object"]
            #     d_url["oname"] = row["object_name"]
            #     row["interface_load_url"] = url % d_url
            # mac_counter

            #print(num, "row", row, type(row))
            yield num, "managed_object_id", 0
            yield num, "managed_object_bi_id", row["managed_object"]
            for c in columns:
                if num == 1:
                    x = row.get(c, "")
                    print("c", c, x, type(x))
                yield num, c, row.get(c, "")
            num += 1
