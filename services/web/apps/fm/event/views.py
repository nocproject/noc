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

# Third-party modules
from django.http import HttpResponse
import orjson

# NOC modules
from noc.config import config
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
    DEFAULT_EVENT_INTERVAL = 3

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
                    where_list += [f"managed_object_bi_id={v.bi_id}"]
                elif k == "managed_object__in":
                    v = [str(id) for id in v]
                    if v:
                        where_list += [f"managed_object_bi_id in ({','.join(v)})"]
                    else:
                        where_list += ["managed_object_bi_id in (-1)"]
                elif k == "event_class":
                    where_list += [f"event_class_bi_id={EventClass.get_by_id(v).bi_id}"]
            return where_list

        def update_event(event, data):
            # event = get_event(id)
            # if not event:
            #     return self.response_not_found()
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
            data["managed_object_address"] = mo.address
            data["managed_object_profile"] = mo.profile.name
            data["managed_object_platform"] = mo.platform.name if mo.platform else ""
            data["managed_object_version"] = mo.version.version if mo.version else ""
            data["segment"] = mo.segment.name
            data["segment_id"] = str(mo.segment.id)
            data["tags"] = mo.labels
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
            data.update(dd)
            # Get alarms
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
                if alarms:
                    row_class = AlarmSeverity.get_severity_css_class_name(get_severity(alarms))
                    data["alarms"] = alarms
                    data["row_class"] = row_class
            # Apply plugins
            if event.event_class.plugins:
                plugins = []
                for p in event.event_class.plugins:
                    if p.name in self.plugins:
                        plugin = self.plugins[p.name]
                        dd = plugin.get_data(event, p.config)
                        if "plugins" in dd:
                            plugins += dd["plugins"]
                            del dd["plugins"]
                        date.update(dd)
                if plugins:
                    data["plugins"] = plugins
            return {data["id"]:data}
        q = self.parse_request_query(request)
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
        # Apply date filter
        start_ts = q.pop("timestamp__gte", None)
        end_ts = q.pop("timestamp__lte", None)
        if start_ts:
            start_ts = datetime.datetime.strptime(start_ts, "%Y-%m-%dT%H:%M:%S")
        if end_ts:
            end_ts = datetime.datetime.strptime(end_ts, "%Y-%m-%dT%H:%M:%S")
        if not end_ts:
            end_ts = datetime.datetime.now()
        if not start_ts:
            start_ts = end_ts - datetime.timedelta(days=self.DEFAULT_EVENT_INTERVAL)
        order_list = []
        if request.is_extjs and self.sort_param in q:
            for r in self.deserialize(q[self.sort_param]):
                # ignoring sort by those fields
                if r["property"] in ("subject", "alarms", "repeats", "duration"):
                    continue
                if r["direction"] == "DESC":
                    order_list += [f"{r['property']} {r['direction']}"]
                else:
                    order_list += [f"{r['property']} {r['direction']}"]
        order_list = order_list or self.default_ordering
        order_section = ""
        if order_list:
            order_section = "ORDER BY " + ", ".join(order_list)
        limit_section = f"LIMIT {limit} OFFSET {start}"
        q = self.cleaned_query(q)
        where_section = make_where_section(q)
        if where_section:
            where_section = " AND " + " AND ".join(where_section)
        # Execute query to clickhouse
        sql = f"""SELECT
            e.event_id as id,
            e.ts as timestamp,
            e.event_class as event_class_bi_id,
            e.managed_object as managed_object_bi_id,
            dictGet('noc_dict.eventclass', ('name'), e.event_class) as event_class,
            dictGet('noc_dict.vendor', ('name'), e.vendor) as vendor,
            dictGet('noc_dict.administrativedomain', ('id','name'), e.administrative_domain) as administrative_domain,
            dictGet('noc_dict.pool', ('name'), e.pool) as pool,
            dictGet('noc_dict.managedobject', ('id', 'name', 'address', 'profile', 'platform', 'version'), e.managed_object) as managed_object,
            e.start_ts as start_timestamp,
            e.source, e.date, e.raw_vars, e.resolved_vars, e.vars,
            d.alarms as alarms
            FROM events e
            LEFT OUTER JOIN (
            SELECT event_id, groupArray(alarm_id) as alarms FROM disposelog  WHERE date >= %s AND date <= %s AND alarm_id != ''  GROUP BY event_id) as d
            ON e.event_id == d.event_id
            WHERE date >= %s AND date <= %s AND ts >= %s AND ts <= %s
            {where_section or ''}
            {order_section}
            {limit_section}
            format JSON
        """
        cursor = connection()
        res = orjson.loads(
            cursor.execute(
                sql,
                return_raw=True,
                args=[
                    start_ts.date().isoformat(),
                    end_ts.date().isoformat(),
                    start_ts.date().isoformat(),
                    end_ts.date().isoformat(),
                    start_ts.replace(microsecond=0).isoformat(),
                    end_ts.replace(microsecond=0).isoformat(),
                ],
            )
        )
        out = []
        d = {}
        for r in res["data"]:
            event = ActiveEvent.create_from_dict(r)
            d = {
                "id": r["id"],
                "managed_object": r["managed_object"]["id"],
                "managed_object__label": r["managed_object"]["name"],
                "managed_object_address": r["managed_object"]["address"],
                "managed_object_profile": r["managed_object"]["profile"],
                "managed_object_platform": r["managed_object"]["platform"],
                "managed_object_version": r["managed_object"]["version"],
                "administrative_domain": r["administrative_domain"]["id"],
                "administrative_domain__label": r["administrative_domain"]["name"],
                "segment": event.managed_object.segment.name,
                "segment_id": event.managed_object.segment.id,
                "tags": event.managed_object.labels,
                "event_class": str(event.event_class.id),
                "event_class__label": event.event_class.name,
                "timestamp": r["timestamp"],
                "source": r["source"],
                "subject": event.subject,
                "repeats": event.repeats,
                "duration": event.duration,
            }
            out += [update_event(event, d)]
        # Format data
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
                total = res["rows_before_limit_at_least"]  # res["statistics"]["rows_read"]
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

    """
    def instance_to_dict_list(self, o, fields=None, nocustom=False):
        row_class = None
        if o.status in ("A", "S"):
            subject = o.subject
            repeats = o.repeats
            duration = o.duration
            alarms = [str(a) for a in o.alarms]
            if alarms:
                row_class = AlarmSeverity.get_severity_css_class_name(get_severity(alarms))
        else:
            subject = None
            repeats = None
            duration = None
            alarms = None
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
            "date": o.timestamp.date().isoformat(),
            "source": o.source,
            "subject": subject,
            "repeats": repeats,
            "duration": duration,
            "alarms": alarms,
            "row_class": row_class,
        }
        if fields:
            d = {k: d[k] for k in fields}
        return d
    """

    def queryset(self, request, query=None):
        """
        Filter records for lookup
        """
        status = request.GET.get("status", "A")
        if status not in self.model_map:
            raise Exception("Invalid status")
        model = self.model_map[status]
        return model.objects




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
        url=r"^(?P<id>[0-9a-f]{24})&date=(?P<date>\d+-\d+-\d+)&managed_object=(?P<mo>\d+)&source=(?P<source>syslog|SNMP Trap)/?$",
        access="read",
        api=True,
    )
    def api_read(self, request, id, date, mo, source):
        """
        Returns dict with event's fields and values
        """
        mo_bi_id = ManagedObject.get_by_id(mo).bi_id
        event = get_event(id, date, mo_bi_id, source)
        if not event:
            return HttpResponse("", status=self.NOT_FOUND)
        return self.response(self.instance_to_dict(event), status=self.OK)
