# ---------------------------------------------------------------------
# fm.event application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
import inspect
import re
import orjson

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.fm.models.activeevent import ActiveEvent
from noc.fm.models.archivedevent import ArchivedEvent
from noc.fm.models.failedevent import FailedEvent
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

    def cleaned_query(self, q):
        q = super().cleaned_query(q)
        if "administrative_domain" in q:
            ad = AdministrativeDomain.objects.get(id=q["administrative_domain"])
            q["managed_object__in"] = list(
                ManagedObject.objects.filter(
                    administrative_domain__in=AdministrativeDomain.get_nested_ids(ad.id)
                ).values_list("id", flat=True)
            )
            del q["administrative_domain"]
        if "resource_group" in q:
            rgs = ResourceGroup.get_by_id(q["resource_group"])
            s = set(
                ManagedObject.objects.filter(
                    effective_service_groups__overlap=ResourceGroup.get_nested_ids(rgs)
                ).values_list("id", flat=True)
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
