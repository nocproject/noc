# ---------------------------------------------------------------------
# inv.macdb application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from typing import Optional, List

# Third-party modules
import orjson

# NOC modules
from noc.services.web.base.extdocapplication import ExtApplication, view
from noc.sa.models.managedobject import ManagedObject
from noc.sa.interfaces.base import MACAddressParameter
from noc.core.mac import MAC
from noc.core.clickhouse.connect import connection
from noc.core.validators import is_mac
from noc.core.translation import ugettext as _
from noc.main.models.pool import Pool
from noc.config import config
from noc.bi.models.macdb import MACDB
from noc.bi.models.mac import MAC as MACHISTORY
from noc.inv.models.interfaceprofile import InterfaceProfile


class MACApplication(ExtApplication):
    """
    MAC application
    """

    title = _("MacDB")
    menu = _("Mac DB")

    mac_search_re = re.compile(r"([\dABCDEF][\dABCDEF]:){3,6}", re.IGNORECASE)
    mac_search_re_inv = re.compile(r"(:[\dABCDEF][\dABCDEF]){2,6}", re.IGNORECASE)

    def parse_result(self):
        """"""

    @classmethod
    def parse_mac_query(cls, query: str) -> str:
        """
        MAC Address Condition:
        * XX:XX:XX:XX:XX:XX -
        """
        if not query:
            mac_query = None
        elif is_mac(query):
            mac_query = f"mac = {int(MAC(MACAddressParameter(accept_bin=False).clean(query)))}"
        elif cls.mac_search_re.match(query):
            mac_query = f"MACNumToString(mac) like '{query}%'"
        elif cls.mac_search_re_inv.match(query):
            mac_query = f"MACNumToString(mac) like '%{query}'"
        else:
            raise ValueError("Unknown query string")
        return mac_query

    @classmethod
    def get_filter(
        cls,
        mac_query: Optional[str] = None,
        managed_object: Optional[int] = None,
        segment: Optional[str] = None,
        interface_profile: Optional[str] = None,
        is_uni: Optional[bool] = None,
    ) -> List[str]:
        """"""
        r = []
        if mac_query:
            r.append(mac_query)
        if managed_object:
            mo = ManagedObject.get_by_id(managed_object)
            r.append(f"managed_object = {mo.bi_id}")
        if segment:
            r.append(f"segment = {segment}")
        if interface_profile:
            p = InterfaceProfile.get_by_id(interface_profile)
            r.append(f"interface_profile = {p.bi_id}")
        return r

    def macdb_query(
        self,
        mac_query: str,
        managed_object: Optional[int] = None,
        segment: Optional[str] = None,
        interface_profile: Optional[str] = None,
        is_uni: Optional[bool] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ):

        limit = limit or 50

        sql = [
            f"SELECT last_seen, managed_object, interface,"
            f" dictGetString('{config.clickhouse.db_dictionaries}.interfaceattributes', 'description', (managed_object, interface)) as description,"
            f" MACNumToString(mac) as mac_s, vlan FROM {MACDB._get_db_table()}",
        ]
        filter_x = self.get_filter(mac_query, managed_object, segment, interface_profile, is_uni)
        if filter_x:
            sql += ["WHERE %s" % " AND ".join(filter_x)]
        sql += ["ORDER BY mac"]
        if limit and offset:
            sql += [f"LIMIT {offset}, {limit}"]
        else:
            sql += [f"LIMIT {limit}"]
        sql += ["FORMAT JSON"]
        sql = " ".join(sql)
        ch = connection()
        r = ch.execute(sql, return_raw=True)
        r = orjson.loads(r)
        mos = {
            mo[1]: mo
            for mo in ManagedObject.objects.filter(
                bi_id__in=[int(x["managed_object"]) for x in r["data"]]
            ).values_list("name", "bi_id", "id", "pool", "object_profile", "object_profile__name")
        }
        out = []
        rows_count = r["rows_before_limit_at_least"]
        for d in r["data"]:
            if int(d["managed_object"]) not in mos:
                rows_count -= 1
                continue
            mo_name, _, mo_id, pool, op, op_name = mos[int(d["managed_object"])]
            pool = Pool.get_by_id(pool)
            out.append(
                {
                    "last_changed": d["last_seen"],
                    "mac": d["mac_s"],
                    # "l2_domain": str(mo.l2_domain),
                    "l2_domain": None,
                    # "l2_domain__label": getattr(mo.l2_domain, "name", ""),
                    "vlan": d["vlan"],
                    "managed_object": str(mo_id),
                    "managed_object__label": str(mo_name),
                    "interface": str(d["interface"]),
                    "description": d["description"],
                    "pool": str(pool),
                    "pool__label": pool.name,
                    "object_profile": str(op),
                    "object_profile__label": op_name or "",
                }
            )
        return out, rows_count

    @view(method=["GET", "POST"], url="^$", access="read", api=True)
    def api_list(self, request):
        q = self.parse_request_query(request)
        query = q.get("__query")
        start = q.get("__start")
        limit = q.get("__limit")
        try:
            mac_query = self.parse_mac_query(query)
        except ValueError as e:
            return self.response(
                {"success": False, "data": [], "message": str(e)}, status=self.BAD_REQUEST
            )
        out, total = self.macdb_query(
            mac_query=mac_query,
            managed_object=q.get("managed_object"),
            interface_profile=q.get("interface_profile"),
            segment=q.get("segment"),
            offset=start,
            limit=limit,
        )
        return self.response({"total": total, "success": True, "data": out}, status=self.OK)

    @classmethod
    def mac_history_query(
        cls,
        mac_query: str,
        managed_object: Optional[int] = None,
        segment: Optional[str] = None,
        interface_profile: Optional[str] = None,
        is_uni: Optional[bool] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ):
        sql = [
            f"SELECT ts, managed_object, interface, MACNumToString(mac) as mac_s, vlan, "
            f" dictGetString('{config.clickhouse.db_dictionaries}.interfaceattributes', 'description', (managed_object, interface)) as description"
            f" FROM {MACHISTORY._get_db_table()}",
        ]
        filter_x = cls.get_filter(mac_query, managed_object, segment, interface_profile, is_uni)
        if filter_x:
            sql += ["WHERE %s" % " AND ".join(filter_x)]
        sql += ["ORDER BY ts DESC"]
        if limit and offset:
            sql += [f"LIMIT {offset}, {limit}"]
        elif limit:
            sql += [f"LIMIT {limit}"]
        sql += ["FORMAT JSON"]
        sql = " ".join(sql)
        ch = connection()
        r = ch.execute(sql, return_raw=True)
        r = orjson.loads(r)
        return r

    @view(url="^(?P<mac>[0-9A-F:]+)/$", method=["GET"], access="view", api=True)
    def api_get_maclog(self, request, mac):
        """GET maclog"""

        out = []
        mac_query = self.parse_mac_query(mac)
        r = self.mac_history_query(mac_query)
        mos = {
            mo[1]: mo
            for mo in ManagedObject.objects.filter(
                bi_id__in=[int(x["managed_object"]) for x in r["data"]]
            ).values_list("name", "bi_id", "id", "pool", "object_profile", "object_profile__name")
        }
        for d in r["data"]:
            if int(d["managed_object"]) not in mos:
                continue
            mo_name, _, mo_id, pool, op, op_name = mos[int(d["managed_object"])]
            pool = Pool.get_by_id(pool)
            out += [
                {
                    "timestamp": str(d["ts"]),
                    "mac": d["mac_s"],
                    "l2_domain": "",
                    "vlan": d["vlan"],
                    "managed_object_name": mo_name,
                    "interface_name": d["interface"],
                    "description": d["description"],
                    "pool": pool.name,
                    "object_profile": op_name,
                }
            ]
        return self.response(out, status=self.OK)

    @view(url="^/history/(?P<mac>[0-9A-F:]+)/$", method=["GET"], access="view", api=True)
    def api_get_maclog(self, request, mac):
        """GET maclog"""

        out = []
        mac_query = self.parse_mac_query(mac)
        r = self.mac_history_query(mac_query)
        mos = {
            mo[1]: mo
            for mo in ManagedObject.objects.filter(
                bi_id__in=[int(x["managed_object"]) for x in r["data"]]
            ).values_list("name", "bi_id", "id", "pool", "object_profile", "object_profile__name")
        }
        rows_count = r["rows_before_limit_at_least"]
        for d in r["data"]:
            if int(d["managed_object"]) not in mos:
                rows_count -= 1
                continue
            mo_name, _, mo_id, pool, op, op_name = mos[int(d["managed_object"])]
            pool = Pool.get_by_id(pool)
            out += [
                {
                    "last_changed": d["last_seen"],
                    "mac": d["mac_s"],
                    # "l2_domain": str(mo.l2_domain),
                    "l2_domain": None,
                    # "l2_domain__label": getattr(mo.l2_domain, "name", ""),
                    "vlan": d["vlan"],
                    "managed_object": str(mo_id),
                    "managed_object__label": str(mo_name),
                    "interface": str(d["interface"]),
                    "description": d["description"],
                    "pool": str(pool),
                    "pool__label": pool.name,
                    "object_profile": str(op),
                    "object_profile__label": op_name or "",
                }
            ]
        return self.response({"total": rows_count, "success": True, "data": out}, status=self.OK)
