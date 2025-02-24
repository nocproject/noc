# ---------------------------------------------------------------------
# fm.event application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
from typing import Dict, Any, Tuple, Optional, List

# Third-party modules
import orjson
from jinja2 import Template

# NOC modules
from noc.services.web.base.extapplication import ExtApplication, view
from noc.fm.models.eventclass import EventClass
from noc.sa.models.managedobject import ManagedObject
from noc.core.fm.event import Event
from noc.bi.models.events import Events
from noc.core.escape import json_escape
from noc.core.clickhouse.connect import connection
from noc.config import config
from noc.core.translation import ugettext as _


class EventApplication(ExtApplication):
    """
    fm.event application
    """

    title = _("Events")
    menu = _("Events")
    icon = "icon_find"
    ignored_params = ["status", "_dc"]

    @view(method=["GET", "POST"], url="^$", access="read", api=True)
    def api_list(self, request):
        q = self.parse_request_query(request)
        query = q.get("__query")
        start = q.get("__start") or 0
        limit = q.get("__limit") or 50
        if limit is None:
            return self.response(
                {"success": False, "message": f"Invalid {self.limit_param} param"},
                status=self.BAD_REQUEST,
            )
        if start is None:
            return self.response(
                {"success": False, "message": f"Invalid {self.start_param} param"},
                status=self.BAD_REQUEST,
            )
        out, total = self.event_query(
            managed_object=q.get("managed_object"),
            segment=q.get("segment"),
            offset=start,
            limit=limit,
        )
        return self.response({"total": total, "success": True, "data": out}, status=self.OK)

    @classmethod
    def get_filter(
        cls,
        managed_object: Optional[int] = None,
        segment: Optional[str] = None,
        from_query: Optional[datetime.date] = None,
        to_query: Optional[datetime.date] = None,
        groups: Optional[List[str]] = None,
        event_class: Optional[str] = None,
    ) -> str:
        """"""
        return ""

    @classmethod
    def event_query(
        cls,
        managed_object: Optional[int] = None,
        segment: Optional[str] = None,
        from_query: Optional[datetime.date] = None,
        to_query: Optional[datetime.date] = None,
        groups: Optional[List[str]] = None,
        event_class: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ):
        """ """
        sql = [
            f"SELECT  e.event_id as id, e.ts as timestamp, nullIf(e.event_class, 0) as event_class_bi_id,"
            f" nullIf(e.managed_object, 0) as managed_object_bi_id, e.target as target, e.target_name as target_name,"
            f" IPv4NumToString(e.ip) as address, e.snmp_trap_oid as snmp_trap_oid, e.raw_vars as raw_vars,"
            f" dictGet('{config.clickhouse.db_dictionaries}.pool', 'name', e.pool) as pool_name,"
            f" dictGetOrNull('{config.clickhouse.db_dictionaries}.eventclass', ('id', 'name'), e.event_class) as event_class,"
            f" dictGetOrNull('{config.clickhouse.db_dictionaries}.managedobject', ('id', 'name'), e.managed_object) as managed_object,"
            f" dictGetOrNull('{config.clickhouse.db_dictionaries}.administrativedomain', ('id', 'name'), e.administrative_domain) as administrative_domain,"
            f" e.source, e.vars, e.labels, e.message, e.data, e.remote_system, e.remote_id"
            f" FROM {Events._get_db_table()} AS e",
        ]
        filter_x = cls.get_filter(
            managed_object, segment, from_query, to_query, groups, event_class
        )
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
        mos = {
            mo[1]: mo
            for mo in ManagedObject.objects.filter(
                bi_id__in=[int(x["managed_object_bi_id"]) for x in r["data"]]
            ).values_list(
                "name", "bi_id", "address", "id", "pool", "administrative_domain__name", "segment"
            )
        }
        rows_count = r["rows_before_limit_at_least"]
        out = []
        for d in r["data"]:
            r = {
                "id": str(d["id"]),
                "timestamp": d["timestamp"],
                "source": d["source"],
                "target": d["target_name"],
                "target_id": d["target"],
                "managed_object_id": None,
                "address": d["address"],
                "segment": None,
                "administrative_domain": None,
                "event_class": None,
                "event_class_id": None,
                "row_class": None,
                "message": d["message"],
                "snmp_trap_oid": d["snmp_trap_oid"],
                "labels": d["labels"],
                "vars": d["vars"],
                "raw_vars": d["raw_vars"],
                "data": [],
                "remote_id": d["remote_id"] or None,
                "remote_system": d["remote_system"] or None,
                "dispose": False,
                "object": None,
            }
            if d["administrative_domain"]:
                r |= {"administrative_domain": r["administrative_domain"]["name"]}
            if d["managed_object_bi_id"] in mos:
                mo_name, _, address, mo_id, pool, ad, ad_name, seg = mos[int(d["managed_object"])]
                r |= {
                    "target": mo_name,
                    "address": address,
                    "managed_object_id": mo_id,
                    "object": {"name": mo_name, "address": address},
                }
            if d["event_class_bi_id"]:
                ec = EventClass.get_by_bi_id(d["event_class_bi_id"])
                r |= {"event_class": ec.name, "event_class_id": str(ec.id)}
            if d["data"]:
                r["data"] = orjson.loads(d["data"])
            out += [r]
        return out, rows_count

    @view(url=r"^(?P<id>[a-z0-9]{24})/reclassify/$", method=["POST"], api=True, access="reclassify")
    def api_reclassify(self, request, id):
        return {"status": True}

    @view(url=r"^(?P<id>[a-z0-9]{24})/json/$", method=["GET"], api=True, access="launch")
    def api_json(self, request, id):
        return {"status": True}
