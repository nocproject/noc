# ---------------------------------------------------------------------
# fm.event application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import os
import inspect
import re
import orjson

# Third-party modules
from django.http import HttpResponse

# NOC modules
from noc.core.clickhouse.connect import connection
from noc.services.web.base.extdocapplication import ExtDocApplication, view
from noc.fm.models.activeevent import ActiveEvent
from noc.fm.models.archivedevent import ArchivedEvent
from noc.fm.models.failedevent import FailedEvent
from noc.fm.models.eventclass import EventClass
from noc.fm.models.alarmseverity import AlarmSeverity
from noc.fm.models.mib import MIB
from noc.fm.models.utils import get_alarm, get_event, get_severity
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.inv.models.resourcegroup import ResourceGroup
from noc.sa.interfaces.base import ModelParameter, UnicodeParameter, DateTimeParameter
from noc.core.escape import json_escape
from noc.core.comp import smart_text
from noc.core.translation import ugettext as _


class EventApplication(ExtDocApplication):
    """
    fm.event application
    """

    title = _("Events")
    menu = _("Events")
    model = ActiveEvent
    icon = "icon_find"

    model_map = {"A": ActiveEvent, "F": FailedEvent, "S": ArchivedEvent}

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

    def list_data(self, request, formatter):
        """
        Returns a list of events
        """

        def make_where_section(query_params):
            where_list = []
            for k, v in query_params.items():
                if k == "timestamp__gte":
                    where_list += [f"timestamp>='{v}'"]
                elif k == "timestamp__lte":
                    where_list += [f"timestamp<='{v}'"]
                elif k == "managed_object":
                    where_list += [f"managed_object={v.bi_id}"]
                elif k == "managed_object__in":
                    v = [str(id) for id in v]
                    if v:
                        where_list += [f"managed_object in ({','.join(v)})"]
                    else:
                        where_list += ["managed_object in (-1)"]
                elif k == "event_class":
                    where_list += [f"event_class={EventClass.get_by_id(v).bi_id}"]
            if where_list:
                return "where " + " and ".join(where_list)
            else:
                return ""

        if request.method == "POST":
            if self.site.is_json(request.META.get("CONTENT_TYPE")):
                q = self.deserialize(request.body)
            else:
                q = {str(k): v[0] if len(v) == 1 else v for k, v in request.POST.lists()}
        else:
            q = {str(k): v[0] if len(v) == 1 else v for k, v in request.GET.lists()}
        # Apply row limit if necessary
        limit = q.get(self.limit_param, self.unlimited_row_limit)
        if limit:
            try:
                limit = max(int(limit), 0)
            except ValueError:
                return HttpResponse(400, "Invalid %s param" % self.limit_param)
        if limit and limit < 0:
            return HttpResponse(400, "Invalid %s param" % self.limit_param)
        start = q.get(self.start_param) or 0
        if start:
            try:
                start = max(int(start), 0)
            except ValueError:
                return HttpResponse(400, "Invalid %s param" % self.start_param)
        elif start and start < 0:
            return HttpResponse(400, "Invalid %s param" % self.start_param)
        # Apply row limit if necessary
        if self.row_limit:
            limit = min(limit or self.row_limit, self.row_limit + 1)
        order_list = []
        if request.is_extjs and self.sort_param in q:
            for r in self.deserialize(q[self.sort_param]):
                if r["direction"] == "DESC":
                    order_list += [f"{r['property']} {r['direction']}"]
                else:
                    order_list += [f"{r['property']} {r['direction']}"]
        order_list = order_list or self.default_ordering
        if order_list:
            order_section = "order by " + ", ".join(order_list)
        else:
            order_section = ""
        limit_section = f"limit {limit} offset {start}"
        q = self.cleaned_query(q)
        where_section = make_where_section(q)
        # Execute query to clickhouse
        sql = f"""select
            e.event_id as id,
            e.ts as timestamp,
            e.event_class as event_class_bi_id,
            e.managed_object as managed_object_bi_id,
            e.start_ts as start_timestamp,
            e.source, e.raw_vars, e.resolved_vars, e.vars
            from events e
            {where_section}
            {order_section}
            {limit_section}
            format JSON
        """
        cursor = connection()
        res = orjson.loads(cursor.execute(sql, return_raw=True, args=[]))
        events = []
        for r in res["data"]:
            events += [
                ActiveEvent(
                    id=r["id"],
                    timestamp=datetime.datetime.strptime(r["timestamp"], "%Y-%m-%d %H:%M:%S"),
                    managed_object=ManagedObject.get_by_bi_id(r["managed_object_bi_id"]),
                    event_class=EventClass.get_by_bi_id(r["event_class_bi_id"]),
                    start_timestamp=datetime.datetime.strptime(
                        r["start_timestamp"], "%Y-%m-%d %H:%M:%S"
                    ),
                    source=r["source"],
                    raw_vars=r["raw_vars"],
                    resolved_vars=r["resolved_vars"],
                    vars=r["vars"],
                )
            ]
        # Format data
        out = [formatter(o) for o in events]
        if self.row_limit and len(out) > self.row_limit + 1:
            return self.response(
                "System records limit exceeded (%d records)" % self.row_limit, status=self.TOO_LARGE
            )
        # Bulk update result. Enrich with proper fields
        out = self.clean_list_data(out)
        #
        if request.is_extjs:
            ld = len(out)
            if limit and (ld == limit or start > 0):
                total = res["statistics"]["rows_read"]
            else:
                total = ld
            out = {"total": total, "success": True, "data": out}
        return self.response(out, status=self.OK)

    def cleaned_query(self, q):
        q = super().cleaned_query(q)
        if "administrative_domain" in q:
            ad = AdministrativeDomain.objects.get(id=q["administrative_domain"])
            q["managed_object__in"] = list(
                ManagedObject.objects.filter(
                    administrative_domain__in=AdministrativeDomain.get_nested_ids(ad.id)
                ).values_list("bi_id", flat=True)
            )
            del q["administrative_domain"]
        if "resource_group" in q:
            rgs = ResourceGroup.get_by_id(q["resource_group"])
            s = set(
                ManagedObject.objects.filter(
                    effective_service_groups__overlap=ResourceGroup.get_nested_ids(rgs)
                ).values_list("bi_id", flat=True)
            )
            if "managed_object__in" in q:
                q["managed_object__in"] = list(set(q["managed_object__in"]).intersection(s))
            else:
                q["managed_object__in"] = s
            del q["resource_group"]
        return q

    def instance_to_dict_list(self, o, fields=None, nocustom=False):
        row_class = None
        if o.status in ("A", "S"):
            subject = o.subject
            repeats = o.repeats
            duration = o.duration
            n_alarms = len(o.alarms)
            if n_alarms:
                row_class = AlarmSeverity.get_severity_css_class_name(get_severity(o.alarms))
        else:
            subject = None
            repeats = None
            duration = None
            n_alarms = None
        d = {
            "id": str(o.id),
            "status": o.status,
            "managed_object": o.managed_object.id,
            "managed_object__label": o.managed_object.name,
            "administrative_domain": o.managed_object.administrative_domain_id,
            "administrative_domain__label": o.managed_object.administrative_domain.name,
            "event_class": str(o.event_class.id) if o.status in ("A", "S") else None,
            "event_class__label": o.event_class.name if o.status in ("A", "S") else None,
            "timestamp": self.to_json(o.timestamp),
            "subject": subject,
            "repeats": repeats,
            "duration": duration,
            "alarms": n_alarms,
            "row_class": row_class,
        }
        if fields:
            d = {k: d[k] for k in fields}
        return d

    def queryset(self, request, query=None):
        """
        Filter records for lookup
        """
        status = request.GET.get("status", "A")
        if status not in self.model_map:
            raise Exception("Invalid status")
        model = self.model_map[status]
        return model.objects

    def instance_to_dict(self, event, fields=None, nocustom=False):
        # event = get_event(id)
        # if not event:
        #     return self.response_not_found()
        d = self.instance_to_dict_list(event)
        dd = {
            v: None
            for v in (
                "body",
                "symptoms",
                "probable_causes",
                "recommended_actions",
                "log",
                "vars",
                "resolved_vars",
                "raw_vars",
            )
        }
        if event.status in ("A", "S"):
            dd["body"] = event.body
            dd["symptoms"] = event.event_class.symptoms
            dd["probable_causes"] = event.event_class.probable_causes
            dd["recommended_actions"] = event.event_class.recommended_actions
            # Fill vars
            left = set(event.vars)
            vars = []
            for ev in event.event_class.vars:
                if ev.name in event.vars:
                    vars += [(ev.name, event.vars[ev.name], ev.description)]
                    left.remove(ev.name)
            vars += [(v, event.vars[v], None) for v in sorted(left)]
            dd["vars"] = vars
            # Fill resolved vars
            vars = []
            is_trap = event.raw_vars.get("source") == "SNMP Trap"
            for v in sorted(event.resolved_vars):
                desc = None
                if is_trap and "::" in v:
                    desc = MIB.get_description(v)
                vars += [(v, event.resolved_vars[v], desc)]
            dd["resolved_vars"] = vars
        dd["raw_vars"] = sorted(event.raw_vars.items())
        # Managed object properties
        mo = event.managed_object
        d["managed_object_address"] = mo.address
        d["managed_object_profile"] = mo.profile.name
        d["managed_object_platform"] = mo.platform.name if mo.platform else ""
        d["managed_object_version"] = mo.version.version if mo.version else ""
        d["segment"] = mo.segment.name
        d["segment_id"] = str(mo.segment.id)
        d["tags"] = mo.labels
        # Log
        if event.log:
            dd["log"] = [
                {
                    "timestamp": self.to_json(ll.timestamp),
                    "from_status": ll.from_status,
                    "to_status": ll.to_status,
                    "message": ll.message,
                }
                for ll in event.log
            ]
        #
        d.update(dd)
        # Get alarms
        if event.status in ("A", "S"):
            alarms = []
            for a_id in event.alarms:
                a = get_alarm(a_id)
                if not a:
                    continue
                if a.opening_event == event.id:
                    role = "O"
                elif a.closing_event == event.id:
                    role = "C"
                else:
                    role = ""
                alarms += [
                    {
                        "id": str(a.id),
                        "status": a.status,
                        "alarm_class": str(a.alarm_class.id),
                        "alarm_class__label": a.alarm_class.name,
                        "subject": a.subject,
                        "role": role,
                        "timestamp": self.to_json(a.timestamp),
                    }
                ]
            d["alarms"] = alarms
        # Apply plugins
        if event.status in ("A", "S") and event.event_class.plugins:
            plugins = []
            for p in event.event_class.plugins:
                if p.name in self.plugins:
                    plugin = self.plugins[p.name]
                    dd = plugin.get_data(event, p.config)
                    if "plugins" in dd:
                        plugins += dd["plugins"]
                        del dd["plugins"]
                    d.update(dd)
            if plugins:
                d["plugins"] = plugins
        elif event.status == "F":
            # Enable traceback plugin for failed events
            d["traceback"] = event.traceback
            d["plugins"] = [("NOC.fm.event.plugins.Traceback", {})]
        return d

    @view(
        url=r"^(?P<id>[a-z0-9]{24})/post/",
        method=["POST"],
        api=True,
        access="launch",
        validate={"msg": UnicodeParameter()},
    )
    def api_post(self, request, id, msg):
        event = get_event(id)
        if not event:
            self.response_not_found()
        event.log_message("%s: %s" % (request.user.username, msg))
        return True

    rx_parse_log = re.compile("^Classified as '(.+?)'.+$")

    @view(url=r"^(?P<id>[a-z0-9]{24})/json/$", method=["GET"], api=True, access="launch")
    def api_json(self, request, id):
        event = get_event(id)
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
        event = get_event(id)
        if not event:
            self.response_not_found()
        if event.status == "N":
            return False
        event.mark_as_new(
            "Event reclassification has been requested " "by user %s" % request.user.username
        )
        return True

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
        sql = """select
            e.event_id as id,
            e.ts as timestamp,
            e.event_class as event_class_bi_id,
            e.managed_object as managed_object_bi_id,
            e.start_ts as start_timestamp,
            e.source, e.raw_vars, e.resolved_vars, e.vars
            from events e
            where event_id=%s
            format JSONEachRow
        """
        cursor = connection()
        res = cursor.execute(sql, return_raw=True, args=[id]).decode().split("\n")
        if not res:
            return HttpResponse("", status=self.NOT_FOUND)
        res = [orjson.loads(r) for r in res if r]
        r = res[0]
        o = ActiveEvent(
            id=r["id"],
            timestamp=datetime.datetime.strptime(r["timestamp"], "%Y-%m-%d %H:%M:%S"),
            managed_object=ManagedObject.get_by_bi_id(r["managed_object_bi_id"]),
            event_class=EventClass.get_by_bi_id(r["event_class_bi_id"]),
            start_timestamp=datetime.datetime.strptime(r["start_timestamp"], "%Y-%m-%d %H:%M:%S"),
            source=r["source"],
            raw_vars=r["raw_vars"],
            resolved_vars=r["resolved_vars"],
            vars=r["vars"],
        )
        return self.response(self.instance_to_dict(o), status=self.OK)
