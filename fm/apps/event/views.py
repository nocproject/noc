# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.event application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import inspect
import re
## NOC modules
from noc.lib.app import ExtApplication, view
from noc.fm.models.newevent import NewEvent
from noc.fm.models.activeevent import ActiveEvent
from noc.fm.models.archivedevent import ArchivedEvent
from noc.fm.models.failedevent import FailedEvent
from noc.fm.models.alarmseverity import AlarmSeverity
from noc.fm.models import get_alarm, get_event
from noc.sa.models.managedobject import ManagedObject
from noc.sa.interfaces.base import (ModelParameter, UnicodeParameter,
                                    DateTimeParameter)
from noc.lib.escape import json_escape


class EventApplication(ExtApplication):
    """
    fm.event application
    """
    title = "Events"
    menu = "Events"
    icon = "icon_find"

    model_map = {
        "N": NewEvent,
        "A": ActiveEvent,
        "F": FailedEvent,
        "S": ArchivedEvent
    }

    clean_fields = {
        "managed_object": ModelParameter(ManagedObject),
        "timestamp": DateTimeParameter()
    }
    ignored_params = ["status", "_dc"]

    def __init__(self, *args, **kwargs):
        ExtApplication.__init__(self, *args, **kwargs)
        from plugins.base import EventPlugin
        # Load plugins
        self.plugins = {}
        for f in os.listdir("fm/apps/event/plugins/"):
            if (not f.endswith(".py") or
                        f == "base.py" or f.startswith("_")):
                continue
            mn = "noc.fm.apps.event.plugins.%s" % f[:-3]
            m = __import__(mn, {}, {}, "*")
            for on in dir(m):
                o = getattr(m, on)
                if (inspect.isclass(o) and
                        issubclass(o, EventPlugin) and
                        o.__module__.startswith(mn)):
                    assert o.name
                    self.plugins[o.name] = o(self)

    def cleaned_query(self, q):
        q = q.copy()
        for p in self.ignored_params:
            if p in q:
                del q[p]
        for p in (
            self.limit_param, self.page_param, self.start_param,
            self.format_param, self.sort_param, self.query_param,
            self.only_param):
            if p in q:
                del q[p]
        # Normalize parameters
        for p in q:
            qp = p.split("__")[0]
            if qp in self.clean_fields:
                q[p] = self.clean_fields[qp].form_clean(q[p])
        return q

    def instance_to_dict(self, o, fields=None):
        row_class = None
        if o.status in ("A", "S"):
            subject = o.get_translated_subject("en")
            repeats = o.repeats
            duration = o.duration
            n_alarms = len(o.alarms)
            if n_alarms:
                severity = 0
                for a in o.alarms:
                    alarm = get_alarm(a)
                    if alarm:
                        severity = max(severity, alarm.severity)
                s = AlarmSeverity.get_severity(severity)
                row_class = s.style.css_class_name
        else:
            subject = None
            repeats = None
            duration = None
            n_alarms = None
        return {
            "id": str(o.id),
            "status": o.status,
            "managed_object": o.managed_object.id,
            "managed_object__label": o.managed_object.name,
            "event_class": str(o.event_class.id) if o.status in ("A", "S") else None,
            "event_class__label": o.event_class.name if o.status in ("A", "S") else None,
            "timestamp": self.to_json(o.timestamp),
            "subject": subject,
            "repeats": repeats,
            "duration": duration,
            "alarms": n_alarms,
            "row_class": row_class
        }

    def queryset(self, request, query=None):
        """
        Filter records for lookup
        """
        status = request.GET.get("status", "A")
        if status not in self.model_map:
            raise Exception("Invalid status")
        model = self.model_map[status]
        return model.objects.all()

    @view(url=r"^$", access="launch", method=["GET"], api=True)
    def api_list(self, request):
        return self.list_data(request, self.instance_to_dict)

    @view(url=r"^(?P<id>[a-z0-9]{24})/$", method=["GET"], api=True,
          access="launch")
    def api_event(self, request, id):
        event = get_event(id)
        if not event:
            self.response_not_found()
        lang = "en"
        d = self.instance_to_dict(event)
        dd = dict((v, None) for v in (
            "body", "symptoms", "probable_causes",
            "recommended_actions", "log",
            "vars", "resolved_vars", "raw_vars"
        ))
        if event.status in ("A", "S"):
            dd["body"] = event.get_translated_body(lang)
            dd["symptoms"] = event.get_translated_symptoms(lang)
            dd["probable_causes"] = event.get_translated_probable_causes(lang)
            dd["recommended_actions"] = event.get_translated_recommended_actions(lang)
            dd["vars"] = sorted(event.vars.items())
            dd["resolved_vars"] = sorted(event.resolved_vars.items())
        dd["raw_vars"] = sorted(event.raw_vars.items())
        # Managed object properties
        mo = event.managed_object
        d["managed_object_address"] = mo.address
        d["managed_object_profile"] = mo.profile_name
        d["managed_object_platform"] = mo.platform
        d["managed_object_version"] = mo.get_attr("version")
        # Log
        if event.log:
            dd["log"] = [
                {
                    "timestamp": self.to_json(l.timestamp),
                    "from_status": l.from_status,
                    "to_status": l.to_status,
                    "message": l.message
                } for l in event.log
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
                alarms += [{
                    "id": str(a.id),
                    "status": a.status,
                    "alarm_class": str(a.alarm_class.id),
                    "alarm_class__label": a.alarm_class.name,
                    "subject": a.get_translated_subject(lang),
                    "role": role,
                    "timestamp": self.to_json(a.timestamp)
                }]
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
            d["plugins"] = [
                ("NOC.fm.event.plugins.Traceback", {})
            ]
        return d

    @view(url=r"^(?P<id>[a-z0-9]{24})/post/", method=["POST"], api=True,
          access="launch", validate={"msg": UnicodeParameter()})
    def api_post(self, request, id, msg):
        event = get_event(id)
        if not event:
            self.response_not_found()
        event.log_message("%s: %s" % (request.user.username, msg))
        return True

    rx_parse_log = re.compile("^Classified as '(.+?)'.+$")

    @view(url=r"^(?P<id>[a-z0-9]{24})/json/$", method=["GET"], api=True,
          access="launch")
    def api_json(self, request, id):
        event = get_event(id)
        if not event:
            self.response_not_found()
        # Get event class
        e_class = None
        if event.status in ("A", "S"):
            for l in event.log:
                match = self.rx_parse_log.match(l.message)
                if match:
                    e_class = match.group(1)
        r = ["["]
        r += ["    {"]
        r += ["        \"profile\": \"%s\"," % json_escape(event.managed_object.profile_name)]
        if e_class:
            r += ["        \"event_class__name\": \"%s\"," % e_class]
        r += ["        \"raw_vars\": {"]
        rr = []
        for k in event.raw_vars:
            if k in ("collector", "severity", "facility"):
                continue
            rr += ["            \"%s\": \"%s\"" % (
                json_escape(k), json_escape(str(event.raw_vars[k])))]
        r += [",\n".join(rr)]
        r += ["        }"]
        r += ["    }"]
        r += ["]"]
        return "\n".join(r)

    @view(url=r"^(?P<id>[a-z0-9]{24})/reclassify/$",
          method=["POST"], api=True, access="launch")
    def api_reclassify(self, request, id):
        event = get_event(id)
        if not event:
            self.response_not_found()
        if event.status == "N":
            return False
        event.mark_as_new(
            "Event reclassification has been requested "
            "by user %s" % request.user.username
        )
        return True
