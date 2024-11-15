# ---------------------------------------------------------------------
# fm.event application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
import datetime

# Python modules
import os
import inspect
import re
from typing import Dict, Any, Tuple, Optional

# Third-party modules
import orjson
from jinja2 import Template
from django.http import HttpResponse

# NOC modules
from noc.services.web.base.extapplication import ExtApplication, view
from noc.fm.models.eventclass import EventClass
from noc.fm.models.alarmseverity import AlarmSeverity
from noc.fm.models.mib import MIB
from noc.fm.models.utils import get_alarm, get_severity
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.sa.interfaces.base import ModelParameter, UnicodeParameter, DateTimeParameter
from noc.inv.models.resourcegroup import ResourceGroup
from noc.core.service.loader import get_service
from noc.core.fm.event import Event
from noc.core.escape import json_escape
from noc.core.comp import smart_text
from noc.core.clickhouse.connect import connection
from noc.config import config
from noc.core.translation import ugettext as _

EVENT_QUERY = f"""
    SELECT
        e.event_id as id,
        e.ts as timestamp,
        nullIf(e.event_class, 0) as event_class_bi_id,
        nullIf(e.managed_object, 0) as managed_object_bi_id,
        e.target as target,
        IPv4NumToString(e.ip) as address,
        dictGet('{config.clickhouse.db_dictionaries}.pool', 'name', e.pool) as pool_name,
        dictGetOrNull('{config.clickhouse.db_dictionaries}.eventclass', ('id', 'name'), e.event_class) as event_class,
        dictGetOrNull('{config.clickhouse.db_dictionaries}.managedobject', ('id', 'name'), e.managed_object) as managed_object,
        e.start_ts as start_timestamp,
        e.source, e.raw_vars, e.resolved_vars, e.vars, e.labels, e.message, e.data,
        d.alarms as alarms
    FROM events e
        LEFT OUTER JOIN (
            SELECT event_id, groupArray(alarm_id) as alarms FROM disposelog  WHERE date >= %%s %s AND alarm_id != ''  GROUP BY event_id) as d
        ON e.event_id == d.event_id
    WHERE date >= %%s AND ts >= %%s %s
    %s
    %s
    LIMIT %%s OFFSET %%s
    FORMAT JSON
"""


class EventApplication(ExtApplication):
    """
    fm.event application
    """

    title = _("Events")
    menu = _("Events")
    icon = "icon_find"

    clean_fields = {
        "managed_object": ModelParameter(ManagedObject),
        "timestamp": DateTimeParameter(),
    }
    ignored_params = ["status", "_dc"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .plugins.base import EventPlugin

        # Load plugins
        self.plugins = {}
        for f in os.listdir("services/web/apps/fm/event/plugins/"):
            if not f.endswith(".py") or f == "base.py" or f.startswith("_"):
                continue
            mn = "noc.services.web.apps.fm.event.plugins.%s" % f[:-3]
            m = __import__(mn, {}, {}, "*")
            for on in dir(m):
                o = getattr(m, on)
                if (
                    inspect.isclass(o)
                    and issubclass(o, EventPlugin)
                    and o.__module__.startswith(mn)
                ):
                    assert o.name
                    self.plugins[o.name] = o(self)

    def get_page(self, q: Dict[str, Any]) -> Tuple[Optional[int], Optional[int]]:
        """
        Getting page: Start and Limit
        :param q:
        :return:
        """
        limit = q.get(self.limit_param, self.unlimited_row_limit)
        if limit:
            try:
                limit = max(int(limit), 0)
            except ValueError:
                return None, None
        if limit and limit < 0:
            return None, None
        # Apply row limit if necessary
        if self.row_limit:
            limit = min(limit or self.row_limit, self.row_limit + 1)
        start = q.get(self.start_param) or 0
        if start:
            try:
                start = max(int(start), 0)
            except ValueError:
                return None, None
        elif start and start < 0:
            return None, None
        return start, limit

    def get_order(self, q: Dict[str, Any]) -> str:
        order_list = []
        for r in self.deserialize(q[self.sort_param]):
            # ignoring sort by those fields
            if r["property"] in ("subject", "alarms", "repeats", "duration"):
                continue
            if r["direction"] == "DESC":
                order_list += [f"{r['property']} {r['direction']}"]
            else:
                order_list += [f"{r['property']} {r['direction']}"]
        order_list = order_list or self.default_ordering
        if not order_list:
            return ""
        return "ORDER BY " + ", ".join(order_list)

    def get_where_section(self, q: Dict[str, Any]) -> str:
        """
        Build where section on query
        :param q:
        :return:
        """
        where_list = []
        if "administrative_domain" in q:
            adm_domain = AdministrativeDomain.objects.get(id=q["administrative_domain"])
            where_list += [
                "administrative_domain IN (%s)"
                % ",".join(str(ad.bi_id) for ad in adm_domain.get_nested())
            ]
        if "resource_group" in q:
            rgs = ResourceGroup.get_by_id(q["resource_group"])
            where_list += [
                "managed_object_bi_id IN (%s)"
                % ",".join(
                    str(mo_bi_id)
                    for mo_bi_id in ManagedObject.objects.filter(
                        effective_service_groups__overlap=ResourceGroup.get_nested_ids(rgs)
                    ).values_list("bi_id", flat=True)
                )
            ]
        if "managed_object" in q:
            mo = ManagedObject.get_by_id(q["managed_object"])
            where_list += [f"managed_object_bi_id = {mo.bi_id}"]
        if "event_class" in q:
            ec = EventClass.get_by_id(q["event_class"])
            where_list += [f"event_class_bi_id = {ec.bi_id}"]
        if not where_list:
            return ""
        return " AND " + " AND ".join(where_list)

    def list_data(self, request, formatter):
        """
        Returns a list of events
        """
        q = self.parse_request_query(request)
        # Apply row limit if necessary
        start, limit = self.get_page(q)
        if limit is None:
            return HttpResponse(400, f"Invalid {self.limit_param} param")
        if start is None:
            return HttpResponse(400, f"Invalid {self.start_param} param")
        # Apply date filter
        start_ts = q.get("timestamp__gte")
        end_ts = q.get("timestamp__lte")
        end_ts_section = ""
        if start_ts:
            start_ts = datetime.datetime.fromisoformat(start_ts)
        if end_ts:
            # AND date <= %%s  AND ts <= %%s
            end_ts = datetime.datetime.fromisoformat(end_ts)
            end_ts_section = (
                f"AND date <= '{end_ts.date().isoformat()}' AND ts <= '{end_ts.isoformat()}'"
            )
        if not start_ts:
            start_ts = datetime.datetime.now().replace(microsecond=0) - datetime.timedelta(days=100)
        # Order section
        if request.is_extjs and self.sort_param in q:
            order_section = self.get_order(q)
        else:
            order_section = "ORDER BY " + ", ".join(self.default_ordering)
        # Where Section
        where_section = self.get_where_section(q)
        # Query
        sql = EVENT_QUERY % (end_ts_section, end_ts_section, where_section, order_section)
        cursor = connection()
        res = orjson.loads(
            cursor.execute(
                sql,
                return_raw=True,
                args=[
                    start_ts.date().isoformat(),
                    start_ts.date().isoformat(),
                    start_ts.isoformat(),
                    limit,
                    start,
                ],
            )
        )
        out = []
        for r in res["data"]:
            if isinstance(r["managed_object"], list):
                # For Clickhouse before 23.XXX
                r["managed_object"] = {"id": r["managed_object"][0], "name": r["managed_object"][1]}
                r["event_class"] = {"id": r["event_class"][0], "name": r["event_class"][1]}
            if not r["managed_object"]["id"] and r["managed_object_bi_id"] and not r["target"]:
                # Unknown object
                self.logger.debug("Unknown managed_object: %s", r)
                mo = ManagedObject.get_by_bi_id(r["managed_object_bi_id"])
                if mo:
                    r["managed_object"] = {"id": str(mo.id), "name": mo.name}
            if not r["event_class"]["id"] and r["event_class_bi_id"]:
                event_class = EventClass.get_by_bi_id(r["event_class_bi_id"])
                r["event_class"] = {"id": str(event_class.id), "name": event_class.name}
            x = formatter(Event.from_json(r))
            alarms = [str(a) for a in r["alarms"]]
            if alarms:
                x["row_class"] = AlarmSeverity.get_severity_css_class_name(get_severity(alarms))
            out.append(x)
        if self.row_limit and len(out) > self.row_limit + 1:
            return self.response(
                "System records limit exceeded (%d records)" % self.row_limit, status=self.TOO_LARGE
            )
        #
        if request.is_extjs:
            ld = len(out)
            if limit and (ld == limit or start > 0):
                total = res["rows_before_limit_at_least"]  # res["statistics"]["rows_read"]
            else:
                total = ld
            out = {"total": total, "success": True, "data": out}
        return self.response(out, status=self.OK)

    @staticmethod
    def render_event_template(template: str, ctx: Dict[str, Any]) -> str:
        s = Template(template).render(ctx)
        if len(s) >= 255:
            s = s[:125] + " ... " + s[-125:]
        return s

    def instance_to_dict_list(self, o: Event, fields=None, nocustom=False):
        event_class = EventClass.get_by_name(o.type.event_class)
        managed_object = ManagedObject.get_by_id(int(o.target.id)) if o.target.id else None
        ctx = {"event": o}
        ctx.update(o.vars)
        d = {
            "id": str(o.id),
            "status": "A",
            "managed_object": managed_object.id if managed_object else o.target.id,
            "managed_object__label": managed_object.name if managed_object else o.target.name,
            "administrative_domain": (
                managed_object.administrative_domain.id if managed_object else None
            ),
            "administrative_domain__label": (
                managed_object.administrative_domain.name if managed_object else ""
            ),
            "event_class": str(event_class.id) if event_class else None,
            "event_class__label": event_class.name if event_class else None,
            "timestamp": self.to_json(o.timestamp),
            "subject": "",
            "repeats": None,
            "duration": None,
            "alarms": [],
            "row_class": None,
        }
        if fields:
            d = {k: d[k] for k in fields}
        if not event_class:
            d["subject"] = o.message
        else:
            d["subject"] = self.render_event_template(event_class.subject_template, ctx)
        return d

    def instance_to_dict(self, event: Event, fields=None, nocustom=False):
        return {}

    @view(
        url=r"^(?P<id>[a-z0-9]{24})/post/",
        method=["POST"],
        api=True,
        access="launch",
        validate={"msg": UnicodeParameter()},
    )
    def api_post(self, request, id, msg):
        event = Event.get_by_id(id)
        if not event:
            self.response_not_found()
        managed_object = ManagedObject.get_by_id(int(event.target.id))
        event_class = EventClass.get_by_name(event.type.event_class)
        ts = datetime.datetime.now().replace(microsecond=0)
        data = {
            "date": ts.date().isoformat(),
            "ts": ts.isoformat(),
            "event_id": str(event.id or ""),
            "op": "new",
            "managed_object": managed_object.bi_id if managed_object else 0,
            "target": event.target.model_dump(exclude={"is_agent"}, exclude_none=True),
            "target_reference": event.target.reference,
            "event_class": event_class.bi_id,
            "message": "%s: %s" % (request.user.username, msg),
        }
        svc = get_service()
        svc.register_metrics("disposelog", [data])
        return True

    rx_parse_log = re.compile("^Classified as '(.+?)'.+$")

    @view(url=r"^(?P<id>[a-z0-9]{24})/json/$", method=["GET"], api=True, access="launch")
    def api_json(self, request, id):
        event = Event.get_by_id(id)
        if not event:
            self.response_not_found()
        # Get event class
        e_class = None
        if event.status in ("A", "S"):
            for ll in event.log:
                match = self.rx_parse_log.match(ll.message)
                if match:
                    e_class = match.group(1)
        r = {"profile": event.managed_object.profile.name}
        if e_class:
            r["event_class__name"] = "%s" % e_class
        r["raw_vars"] = {
            json_escape(k): json_escape(str(event.raw_vars[k]))
            for k in event.raw_vars
            if k not in {"collector", "severity", "facility"}
        }
        if event.source:
            r["raw_vars"]["source"] = event.source
        return smart_text(orjson.dumps(r, option=orjson.OPT_INDENT_2))

    @view(url=r"^(?P<id>[a-z0-9]{24})/reclassify/$", method=["POST"], api=True, access="launch")
    def api_reclassify(self, request, id):
        event = Event.get_by_id(id)
        if not event:
            self.response_not_found()
        if event.target.id:
            managed_object = ManagedObject.get_by_id(int(event.target.id))
            stream, partition = managed_object.events_stream_and_partition
        else:
            managed_object, stream, partition = 0, "events.default", 0
        svc = get_service()
        svc.publish(
            orjson.dumps(event.model_dump()),
            stream=stream,
            partition=partition,
        )
        data = {
            "date": event.timestamp.date(),
            "ts": event.timestamp.isoformat(),
            "event_id": str(event.id or ""),
            "op": "new",
            "managed_object": managed_object.bi_id if managed_object else 0,
            "target": event.target.model_dump(exclude={"is_agent"}, exclude_none=True),
            "target_reference": event.target.reference,
            "event_class": 0,
            "message": f"Event reclassification has been requested by user {request.user.username}",
        }
        svc.register_metrics("disposelog", [data])
        return True

    @view(method=["GET"], url=r"^$", access="read", api=True)
    def api_list(self, request):
        return self.list_data(request, self.instance_to_dict_list)

    @view(
        method=["GET"],
        url=r"^(?P<id>[0-9a-f]{24}|\d+|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/?$",
        access="read",
        api=True,
    )
    def api_read(self, request, id):
        """
        Returns dict with event's fields and values
        """
        event = Event.get_by_id(id)
        if not event:
            return self.response_not_found()

        mo = ManagedObject.get_by_id(int(event.target.id))
        event_class = EventClass.get_by_name(event.type.event_class)
        ctx = {"event": event}
        ctx.update(event.vars)
        d = {
            "id": str(event.id),
            "status": "A",
            "managed_object": event.target.id,
            "managed_object__label": event.target.name,
            "administrative_domain": mo.administrative_domain_id if mo else None,
            "administrative_domain__label": mo.administrative_domain.name if mo else "",
            "event_class": str(event_class.id) if event_class else None,
            "event_class__label": event_class.name if event_class else None,
            "timestamp": self.to_json(event.timestamp),
            "subject": (
                self.render_event_template(event_class.subject_template, ctx) if event_class else ""
            ),
            "repeats": None,
            "duration": None,
            "alarms": [],
            "log": None,
            # Vars
            "raw_vars": sorted([(x.name, x.value) for x in event.data]),
            "vars": [],
            "resolved_vars": [],
            #
            "body": None,
            "symptoms": None,
            "probable_causes": None,
            "recommended_actions": None,
            #
            "plugins": [],
        }
        if event_class:
            d |= {
                "body": self.render_event_template(event_class.subject_template, ctx),
                "symptoms": event_class.symptoms,
                "probable_causes": event_class.probable_causes,
                "recommended_actions": event_class.recommended_actions,
            }
            # Fill vars
            left = set(event.vars)
            for ev in event_class.vars:
                if ev.name in event.vars:
                    d["vars"] += [(ev.name, event.vars[ev.name], ev.description)]
                    left.remove(ev.name)
            d["vars"] += [(v, event.vars[v], None) for v in sorted(left)]
            # Fill resolved vars
            is_trap = event.type.source == "SNMP Trap"
            for v in sorted(event.data, key=lambda x: x.name):
                if v.snmp_raw:
                    continue
                desc = None
                if is_trap and "::" in v.name:
                    desc = MIB.get_description(v.name)
                d["resolved_vars"] += [(v.name, v.value, desc)]
        if not d["raw_vars"]:
            d["raw_vars"] = {v.name: v.value for v in event.data}
        # ManagedObject
        if mo:
            d |= {
                "managed_object_address": mo.address,
                "managed_object_profile": mo.profile.name,
                "managed_object_platform": mo.platform.name if mo.platform else "",
                "managed_object_version": mo.version.version if mo.version else "",
                "segment": mo.segment.name,
                "segment_id": str(mo.segment.id),
                "tags": mo.labels,
            }
        return self.response(d, status=self.OK)
