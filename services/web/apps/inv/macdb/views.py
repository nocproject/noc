# ---------------------------------------------------------------------
# inv.macdb application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from typing import Optional

# Third-party modules
import orjson

# NOC modules
from noc.services.web.base.extdocapplication import ExtApplication, view
from noc.sa.models.managedobject import ManagedObject
from noc.sa.interfaces.base import MACAddressParameter
from noc.core.mac import MAC
from noc.bi.models.macdb import MACDB
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.core.validators import is_mac
from noc.core.translation import ugettext as _


class MACApplication(ExtApplication):
    """
    MAC application
    """

    title = _("MacDB")
    menu = _("Mac DB")

    mac_search_re = re.compile(r"([\dABCDEF][\dABCDEF]:){2,}", re.IGNORECASE)
    mac_search_re_inv = re.compile(r"(:[\dABCDEF][\dABCDEF]){2,}", re.IGNORECASE)

    def parse_result(self):
        """"""

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
        from noc.core.clickhouse.connect import connection

        limit = limit or 50

        sql = [
            "SELECT last_seen, managed_object, interface, mac, vlan FROM %s" % MACDB._get_db_table(),
        ]
        filter_x = []
        if mac_query:
            filter_x.append(mac_query)
        if managed_object:
            mo = ManagedObject.get_by_id(managed_object)
            filter_x.append(f"managed_object = {mo.bi_id}")
        if segment:
            filter_x.append(f"segment = {segment}")
        if interface_profile:
            p = InterfaceProfile.get_by_id(interface_profile)
            filter_x.append(f"interface_profile = {p.bi_id}")
        if filter_x:
            sql += ["WHERE %s" % " AND ".join(filter_x)]
        sql += ["ORDER BY mac"]
        if limit and offset:
            sql += [f"LIMIT {offset}, {limit}"]
        else:
            sql += [f"LIMIT {limit}"]
        sql += ["FORMAT JSON"]
        sql = " ".join(sql)
        print("Run Query", sql)
        ch = connection()
        r = ch.execute(sql, return_raw=True)
        r = orjson.loads(r)
        out = []
        for d in r["data"]:
            mo = ManagedObject.get_by_bi_id(d["managed_object"])
            if not mo:
                continue
            iface = mo.get_interface(d["interface"])
            out.append(
                {
                    "last_changed": d["last_seen"],
                    "mac": str(MAC(int(d["mac"]))),
                    "l2_domain": str(mo.l2_domain),
                    "l2_domain__label": getattr(mo.l2_domain, "name", ""),
                    "vlan": d["vlan"],
                    "managed_object": str(mo),
                    "managed_object__label": str(mo),
                    "interface": str(d["interface"]),
                    "interface__label": str(iface),
                    "description": getattr(iface, "description", ""),
                    "pool": str(mo.pool),
                    "pool__label": getattr(mo.pool, "name", ""),
                    "object_profile": str(mo.object_profile),
                    "object_profile__label": getattr(mo.object_profile, "name", ""),
                }
            )
        return out, r["rows_before_limit_at_least"]

    @view(method=["GET", "POST"], url="^$", access="read", api=True)
    def api_list(self, request):
        q = self.parse_request_query(request)
        print(q)
        query = q.get("__query")
        start = q.get("__start")
        limit = q.get("__limit")
        if not query:
            mac_query = None
        elif is_mac(query):
            mac_query = f"mac = {int(MAC(MACAddressParameter(accept_bin=False).clean(query)))}"
        elif self.mac_search_re.match(query):
            mac_query = f"MACNumToString(mac) like {query}"
        elif self.mac_search_re_inv.match(query):
            mac_query = f"MACNumToString(mac) like {query}"
        else:
            raise ValueError("Unknown query string")
        out, total = self.macdb_query(
            mac_query=mac_query,
            managed_object=q.get("managed_object"),
            interface_profile=q.get("interface_profile"),
            segment=q.get("segment"),
            offset=start, limit=limit,
        )
        return self.response({"total": total, "success": True, "data": out}, status=self.OK)

    @view(url="^(?P<mac>[0-9A-F:]+)/$", method=["GET"], access="view", api=True)
    def api_get_maclog(self, request, mac):
        """GET maclog"""
        out = []
        return self.response(out, status=self.OK)
