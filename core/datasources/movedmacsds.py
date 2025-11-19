# ----------------------------------------------------------------------
# Moved MACs DataSource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import ast
import bisect
import datetime
from operator import itemgetter
import re
from typing import Any, AsyncIterable, Dict, List, Optional, Iterable, Tuple

# NOC modules
from noc.config import config
from noc.core.clickhouse.connect import connection
from noc.core.mac import MAC
from noc.core.translation import ugettext as _
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.inv.models.macvendor import MACVendor
from noc.inv.models.resourcegroup import ResourceGroup
from noc.sa.models.managedobject import ManagedObject
from .base import FieldInfo, FieldType, BaseDataSource, ParamInfo

MULTICAST_MACS = [
    ("01:00:5E:00:00:00", "01:00:5E:FF:FF:FF"),
    ("01:80:C2:00:00:00", "01:80:C2:FF:FF:FF"),
]

DEVICE_MOVED_QUERY = """SELECT
   managed_object, groupArray((ts, serials)) as serial_arr
   FROM managedobjects
   WHERE date = '%s' or date = '%s'
   GROUP BY managed_object HAVING uniq(arraySort(serials)) > 1 ORDER BY managed_object
"""

"""
Find mac, that more 1 unique interface the requested time range groupUniqArray has high
 memory consumption (that groupUniqArray), so used subquery for filter data.
"""
MAC_MOVED_QUERY = """
SELECT
   managed_object,
   smac,
   arrayReduce('groupUniqArray', ifaces),
   arrayReduce('groupUniqArray', migrate_ifaces),
   iface_count
FROM (
  SELECT
     managed_object,
     MACNumToString(mac) as smac,
     groupArray((interface, toUnixTimestamp(ts))) as ifaces,
     groupArray(interface) as migrate_ifaces,
     uniq(interface) as iface_count
     FROM mac
     WHERE %%s and %s and date >= '%%s' and date < '%%s'
     GROUP BY mac, managed_object, vlan
     HAVING iface_count > 1
)
    """ % " AND ".join(
    "(mac < %s or mac > %s)" % (int(MAC(x[0])), int(MAC(x[1]))) for x in MULTICAST_MACS
)

rx_port_num = re.compile(r"\d+$")


def get_interface(ifaces: str):
    r = sorted(ast.literal_eval(ifaces), key=itemgetter(1))
    iface_from, iface_to = r[0][0], r[-1][0]
    if iface_from == iface_to:
        iface_from, iface_to = (
            r[bisect.bisect_left(r, (r[-1][0], 0)) - 1][0],
            r[-1][0],
        )
    return iface_from, iface_to, r[bisect.bisect_left(r, (iface_to, 0))]


class MovedMACsDS(BaseDataSource):
    name = "movedmacsds"
    row_index = "managed_object_id"
    fields = [
        FieldInfo(name="managed_object_id", type=FieldType.UINT),
        FieldInfo(name="managed_object_bi_id"),
        FieldInfo(name="event_type"),
        FieldInfo(name="sn_changed"),
        FieldInfo(name="vendor_mac"),
        FieldInfo(name="mac"),
        FieldInfo(name="migrate_ts"),
        FieldInfo(name="from_iface_name"),
        FieldInfo(name="from_iface_down"),
        FieldInfo(name="to_iface_name"),
        FieldInfo(name="to_iface_down"),
    ]
    params = [
        ParamInfo(name="start", type="datetime", required=True),
        ParamInfo(name="end", type="datetime", required=True),
        ParamInfo(name="segment", type="str", model="inv.NetworkSegment"),
        ParamInfo(name="resource_group", type="str", model="inv.ResourceGroup"),
        ParamInfo(name="interface_profile", type="str", model="inv.InterfaceProfile"),
        ParamInfo(name="exclude_serial_change", type="bool", default=False),
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
        admin_domain_ads: Optional[List[int]] = None,
        start: datetime.datetime = None,
        end: datetime.datetime = None,
        interface_profile: Optional[InterfaceProfile] = None,
        exclude_serial_change: bool = False,
        *args,
        **kwargs,
    ) -> AsyncIterable[Tuple[str, str]]:
        end = end + datetime.timedelta(days=1)
        if interface_profile:
            iface_filter = (
                f"dictGetString('{config.clickhouse.db_dictionaries}.interfaceattributes', "
                f"'profile', (managed_object, interface)) == '{interface_profile.name}'"
            )
        else:
            iface_filter = "is_uni = 1"
        serials_changed = {}
        ch = connection()
        for row in ch.execute(
            DEVICE_MOVED_QUERY
            % (
                start.date().isoformat(),
                (end.date() - datetime.timedelta(days=1)).isoformat(),
            )
        ):
            serials_changed[int(row[0])] = row[1]
        q_filter = cls.get_filter(kwargs)
        mos = ManagedObject.objects.filter(**q_filter)
        if admin_domain_ads:
            mos = mos.filter(administrative_domain__in=admin_domain_ads)
        mos_bi_id = set(mos.order_by("bi_id").values_list("bi_id", flat=True))
        num = 1
        for (
            mo_bi_id,
            mac,
            ifaces,
            migrate_ifaces,
            migrate_count,
        ) in ch.execute(
            MAC_MOVED_QUERY % (iface_filter, start.date().isoformat(), end.date().isoformat())
        ):
            mo_bi_id = int(mo_bi_id)
            if int(mo_bi_id) not in mos_bi_id:
                continue
            if exclude_serial_change and mo_bi_id in serials_changed:
                continue
            iface_from, iface_to, migrate = get_interface(ifaces)
            event_type = _("Migrate")
            if (
                rx_port_num.search(iface_from).group() == rx_port_num.search(iface_to).group()
                and iface_from != iface_to
            ):
                event_type = _("Migrate (Device Changed)")
            mo = ManagedObject.get_by_bi_id(mo_bi_id)
            if not mo:
                continue
            yield num, "managed_object_id", mo.id
            yield num, "managed_object_bi_id", str(mo_bi_id)
            yield num, "event_type", event_type
            yield num, "sn_changed", _("Yes") if mo_bi_id in serials_changed else _("No")
            yield num, "vendor_mac", MACVendor.get_vendor(mac)
            yield num, "mac", mac
            yield num, "migrate_ts", datetime.datetime.fromtimestamp(migrate[1]).isoformat(sep=" ")
            yield num, "from_iface_name", iface_from
            yield num, "from_iface_down", "--"
            yield num, "to_iface_name", iface_to
            yield num, "to_iface_down", "--"
            num += 1
