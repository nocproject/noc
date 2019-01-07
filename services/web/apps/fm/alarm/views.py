# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# fm.alarm application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import os
import inspect
import datetime
import operator
# Third-party modules
import bson
from pymongo import ReadPreference
from mongoengine.errors import DoesNotExist
# NOC modules
from noc.config import config
from noc.lib.app.extapplication import ExtApplication, view
from noc.inv.models.object import Object
from noc.inv.models.networksegment import NetworkSegment
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.fm.models.alarmseverity import AlarmSeverity
from noc.fm.models.activeevent import ActiveEvent
from noc.fm.models.archivedevent import ArchivedEvent
from noc.fm.models.utils import get_alarm
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.selectorcache import SelectorCache
from noc.gis.utils.addr.ru import normalize_division
from noc.main.models import User
from noc.sa.models.useraccess import UserAccess
from noc.sa.interfaces.base import (ModelParameter, UnicodeParameter,
                                    DateTimeParameter, StringParameter)
from noc.maintenance.models.maintenance import Maintenance
from noc.maintenance.models.maintenance import MaintenanceObject
from noc.sa.models.servicesummary import SummaryItem
from noc.fm.models.alarmplugin import AlarmPlugin
from noc.core.translation import ugettext as _
from noc.fm.models.alarmescalation import AlarmEscalation


def get_advanced_field(id):
    from noc.crm.models.subscriberprofile import SubscriberProfile
    from noc.sa.models.serviceprofile import ServiceProfile

    for model, field in ((ServiceProfile, "total_services"), (SubscriberProfile, "total_subscribers")):
        if model.get_by_id(id):
            return field
    return "total_services"


class AlarmApplication(ExtApplication):
    """
    fm.alarm application
    """
    title = _("Alarm")
    menu = _("Alarms")
    glyph = "exclamation-triangle"

    implied_permissions = {
        "launch": ["sa:managedobject:alarm"]
    }

    model_map = {
        "A": ActiveAlarm,
        "C": ArchivedAlarm
    }

    clean_fields = {
        "managed_object": ModelParameter(ManagedObject),
        "timestamp": DateTimeParameter()
    }

    ignored_params = ["status", "_dc"]

    diagnostic_plugin = AlarmPlugin(
        name="diagnostic",
        config={}
    )

    advanced_filter_params = {"service_profile": "total_services",
                              "subscribers_profile": "total_subscribers",
                              "profile": get_advanced_field}

    DEFAULT_ARCH_ALARM = datetime.timedelta(seconds=config.web.api_arch_alarm_limit)

    def __init__(self, *args, **kwargs):
        ExtApplication.__init__(self, *args, **kwargs)
        from .plugins.base import AlarmPlugin
        # Load plugins
        self.plugins = {}
        for f in os.listdir("services/web/apps/fm/alarm/plugins/"):
            if (not f.endswith(".py") or
                    f == "base.py" or
                    f.startswith("_")):
                continue
            mn = "noc.services.web.apps.fm.alarm.plugins.%s" % f[:-3]
            m = __import__(mn, {}, {}, "*")
            for on in dir(m):
                o = getattr(m, on)
                if (inspect.isclass(o) and
                        issubclass(o, AlarmPlugin) and
                        o.__module__.startswith(mn)):
                    assert o.name
                    self.plugins[o.name] = o(self)

    def cleaned_query(self, q):
        q = q.copy()
        status = q["status"] if "status" in q else "A"
        for p in self.ignored_params:
            if p in q:
                del q[p]
        for p in (
                self.limit_param, self.page_param, self.start_param,
                self.format_param, self.sort_param, self.query_param, self.only_param):
            if p in q:
                del q[p]
        # Normalize parameters
        for p in q:
            qp = p.split("__")[0]
            if qp in self.clean_fields:
                q[p] = self.clean_fields[qp].clean(q[p])
        # Advanced filter
        for p in self.advanced_filter_params:
            params = []
            for x in q.keys():
                if x.startswith(p):
                    params += [q[x]]
                    del q[x]
            if params:
                af = self.advanced_filter(self.advanced_filter_params[p], params)
                if "__raw__" in q and "__raw__" in af:
                    # Multiple raw query
                    q["__raw__"].update(af["__raw__"])
                    del af["__raw__"]
                q.update(af)
        # Exclude maintenance
        if "maintenance" not in q:
            q["maintenance"] = "hide"
        if q["maintenance"] == "hide":
            q["managed_object__nin"] = Maintenance.currently_affected()
        elif q["maintenance"] == "only":
            q["managed_object__in"] = Maintenance.currently_affected()
        del q["maintenance"]
        if "administrative_domain" in q:
            if q["administrative_domain"] != '_root_':
                q["adm_path"] = int(q["administrative_domain"])
            q.pop("administrative_domain")
        if "segment" in q:
            if q["segment"] != '_root_':
                q["segment_path"] = bson.ObjectId(q["segment"])
            q.pop("segment")
        if "managedobjectselector" in q:
            s = SelectorCache.objects.filter(selector=q["managedobjectselector"]).values_list("object")
            if "managed_object__in" in q:
                q["managed_object__in"] = list(set(q["managed_object__in"]).intersection(s))
            else:
                q["managed_object__in"] = s
            q.pop("managedobjectselector")
        if "cleared_after" in q:
            q["clear_timestamp__gte"] = datetime.datetime.now() - datetime.timedelta(seconds=int(q["cleared_after"]))
            q.pop("cleared_after")
        #
        if "wait_tt" in q:
            q["wait_tt__exists"] = True
            q["wait_ts__exists"] = False
            del q["wait_tt"]
        #
        if "collapse" in q:
            c = q["collapse"]
            del q["collapse"]
            if c != "0":
                q["root__exists"] = False
        if status == "C":
            if ("timestamp__gte" not in q and "timestamp__lte" not in q and
                    "escalation_tt__contains" not in q and "managed_object" not in q):
                q["timestamp__gte"] = datetime.datetime.now() - self.DEFAULT_ARCH_ALARM
        return q

    def advanced_filter(self, field, params):
        """
        Field: field0=ProfileID,field1=ProfileID:true....
        cq - caps query
        mq - main_query
        field0=ProfileID - Profile is exists
        field0=!ProfileID - Profile is not exists
        field0=ProfileID:true - Summary value equal True
        field0=ProfileID:2~50 - Summary value many then 2 and less then 50

        :param field: Query Field name
        :param params: Query params
        :return:
        """
        q = {}
        # print(field, params)
        c_in = []
        c_nin = []
        for c in params:
            if not c:
                continue
            if "!" in c:
                # @todo Добавить исключение (только этот) !ID
                c_id = c[1:]
                c_query = "nexists"
            elif ":" not in c:
                c_id = c
                c_query = "exists"
            else:
                c_id, c_query = c.split(":", 1)
            try:
                c_id = bson.ObjectId(c_id)
                if callable(field):
                    field = field(c_id)
            except bson.errors.InvalidId as e:
                self.logger.warning(e)
                continue
            if "~" in c_query:
                l, r = c_query.split("~")
                if not l:
                    cond = {"$lt": int(r)}
                elif not r:
                    cond = {"$gt": int(l)}
                else:
                    cond = {"$lt": int(r), "$gt": int(l)}
                q["__raw__"] = {field: {"$elemMatch": {"profile": c_id,
                                                       "summary": cond}}}
            elif c_query == "exists":
                c_in += [c_id]
                continue
            elif c_query == "nexists":
                c_nin += [c_id]
                continue
            else:
                try:
                    c_query = int(c_query)
                    q["__raw__"] = {field: {"$elemMatch": {"profile": c_id,
                                                           "summary": int(c_query)}}}
                except ValueError:
                    q["__raw__"] = {field: {"$elemMatch": {"profile": c_id,
                                                           "summary": {"$regex": c_query}}}}
        if c_in:
            q["%s__profile__in" % field] = c_in
        if c_nin:
            q["%s__profile__nin" % field] = c_nin

        return q

    def instance_to_dict(self, o, fields=None):
        s = AlarmSeverity.get_severity(o.severity)
        n_events = (ActiveEvent.objects.filter(alarms=o.id).count() +
                    ArchivedEvent.objects.filter(alarms=o.id).count())
        mtc = o.managed_object.id in Maintenance.currently_affected()
        if o.status == "C":
            # For archived alarms
            mtc = Maintenance.objects.filter(start__lte=o.clear_timestamp, stop__lte=o.timestamp,
                                             affected_objects__in=[
                                                 MaintenanceObject(object=o.managed_object)]).count() > 0

        d = {
            "id": str(o.id),
            "status": o.status,
            "managed_object": o.managed_object.id,
            "managed_object__label": o.managed_object.name,
            "administrative_domain": o.managed_object.administrative_domain_id,
            "administrative_domain__label": o.managed_object.administrative_domain.name,
            "severity": o.severity,
            "severity__label": s.name,
            "alarm_class": str(o.alarm_class.id),
            "alarm_class__label": o.alarm_class.name,
            "timestamp": self.to_json(o.timestamp),
            "subject": o.subject,
            "events": n_events,
            "duration": o.duration,
            "clear_timestamp": self.to_json(o.clear_timestamp) if o.status == "C" else None,
            "row_class": s.style.css_class_name,
            "segment__label": o.managed_object.segment.name,
            "segment": str(o.managed_object.segment.id),
            "location_1": self.location(o.managed_object.container.id)[0] if o.managed_object.container else "",
            "location_2": self.location(o.managed_object.container.id)[1] if o.managed_object.container else "",
            "escalation_tt": o.escalation_tt,
            "escalation_error": o.escalation_error,
            "platform": o.managed_object.platform.name if o.managed_object.platform else "",
            "address": o.managed_object.address,
            "ack_ts": self.to_json(o.ack_ts),
            "ack_user": o.ack_user,
            "isInMaintenance": mtc,
            "summary": self.f_glyph_summary({
                "subscriber": SummaryItem.items_to_dict(o.total_subscribers),
                "service": SummaryItem.items_to_dict(o.total_services)
            }),
            "total_objects": sum(x.summary for x in o.total_objects),
            "total_subscribers": self.f_summary({"subscriber": SummaryItem.items_to_dict(o.total_subscribers)}),
            "total_services": self.f_summary({"service": SummaryItem.items_to_dict(o.total_services)})
        }
        if fields:
            d = dict((k, d[k]) for k in fields)
        return d

    def queryset(self, request, query=None):
        """
        Filter records for lookup
        """
        status = request.GET.get("status", "A")
        if status not in self.model_map:
            raise Exception("Invalid status")
        model = self.model_map[status]
        if request.user.is_superuser:
            return model.objects.filter(read_preference=ReadPreference.SECONDARY_PREFERRED).all()
        else:
            return model.objects.filter(
                adm_path__in=UserAccess.get_domains(request.user), read_preference=ReadPreference.SECONDARY_PREFERRED
            )

    @view(url=r"^$", access="launch", method=["GET"], api=True)
    def api_list(self, request):
        return self.list_data(request, self.instance_to_dict)

    @view(url=r"^(?P<id>[a-z0-9]{24})/$", method=["GET"], api=True,
          access="launch")
    def api_alarm(self, request, id):
        alarm = get_alarm(id)
        if not alarm:
            self.response_not_found()
        user = request.user
        d = self.instance_to_dict(alarm)
        d["body"] = alarm.body
        d["symptoms"] = alarm.alarm_class.symptoms
        d["probable_causes"] = alarm.alarm_class.probable_causes
        d["recommended_actions"] = alarm.alarm_class.recommended_actions
        d["vars"] = sorted(alarm.vars.items())
        d["status"] = alarm.status
        d["status__label"] = {
            "A": "Active",
            "C": "Cleared"
        }[alarm.status]
        # Managed object properties
        mo = alarm.managed_object
        d["managed_object_address"] = mo.address
        d["managed_object_profile"] = mo.profile.name
        d["managed_object_platform"] = mo.platform.name if mo.platform else ""
        d["managed_object_version"] = mo.version.version if mo.version else ""
        d["segment"] = mo.segment.name
        d["segment_id"] = str(mo.segment.id)
        d["segment_path"] = " | ".join(NetworkSegment.get_by_id(p).name for p in NetworkSegment.get_path(mo.segment))
        if mo.container:
            cp = []
            c = mo.container.id
            while c:
                try:
                    o = Object.objects.get(id=c)
                    if o.container:
                        cp.insert(0, o.name)
                    c = o.container.id if o.container else None
                except DoesNotExist:
                    break
            d["container_path"] = " | ".join(cp)
            if not self.location(mo.container.id)[0]:
                d["address_path"] = None
            else:
                d["address_path"] = ", ".join(self.location(mo.container.id))
        d["tags"] = mo.tags
        # Log
        if alarm.log:
            d["log"] = [
                {
                    "timestamp": self.to_json(l.timestamp),
                    "from_status": l.from_status,
                    "to_status": l.to_status,
                    "message": l.message
                } for l in alarm.log
            ]
        # Events
        events = []
        for ec in ActiveEvent, ArchivedEvent:
            for e in ec.objects.filter(alarms=alarm.id):
                events += [{
                    "id": str(e.id),
                    "event_class": str(e.event_class.id),
                    "event_class__label": e.event_class.name,
                    "timestamp": self.to_json(e.timestamp),
                    "status": e.status,
                    "managed_object": e.managed_object.id,
                    "managed_object__label": e.managed_object.name,
                    "subject": e.subject
                }]
        if events:
            d["events"] = events
        # Alarms
        children = self.get_nested_alarms(alarm)
        if children:
            d["alarms"] = {
                "expanded": True,
                "children": children
            }
        # Subscribers
        if alarm.status == "A":
            d["subscribers"] = self.get_alarm_subscribers(alarm)
            d["is_subscribed"] = user in alarm.subscribers
        # Apply plugins
        plugins = []
        acp = alarm.alarm_class.plugins or []
        acp += [self.diagnostic_plugin]
        for p in acp:
            if p.name in self.plugins:
                plugin = self.plugins[p.name]
                dd = plugin.get_data(alarm, p.config)
                if "plugins" in dd:
                    plugins += dd["plugins"]
                    del dd["plugins"]
                d.update(dd)
        if plugins:
            d["plugins"] = plugins
        return d

    def get_alarm_subscribers(self, alarm):
        """
        JSON-serializable subscribers
        :param alarm:
        :return:
        """
        subscribers = []
        for u in alarm.subscribers:
            try:
                u = User.objects.get(id=u)
                subscribers += [{
                    "id": u.id,
                    "name": " ".join([u.first_name, u.last_name]),
                    "login": u.username
                }]
            except User.DoesNotExist:
                pass
        return subscribers

    def get_nested_alarms(self, alarm):
        """
        Return nested alarms as a part of NodeInterface
        :param alarm:
        :return:
        """
        children = []
        for ac in (ActiveAlarm, ArchivedAlarm):
            for a in ac.objects.filter(root=alarm.id):
                s = AlarmSeverity.get_severity(a.severity)
                c = {
                    "id": str(a.id),
                    "subject": a.subject,
                    "alarm_class": str(a.alarm_class.id),
                    "alarm_class__label": a.alarm_class.name,
                    "managed_object": a.managed_object.id,
                    "managed_object__label": a.managed_object.name,
                    "timestamp": self.to_json(a.timestamp),
                    "iconCls": "icon_error",
                    "row_class": s.style.css_class_name
                }
                nc = self.get_nested_alarms(a)
                if nc:
                    c["children"] = nc
                    c["expanded"] = True
                else:
                    c["leaf"] = True
                children += [c]
        return children

    @view(url=r"^(?P<id>[a-z0-9]{24})/post/", method=["POST"], api=True,
          access="launch", validate={"msg": UnicodeParameter()})
    def api_post(self, request, id, msg):
        alarm = get_alarm(id)
        if not alarm:
            self.response_not_found()
        alarm.log_message("%s: %s" % (request.user.username, msg))
        return True

    @view(url=r"^(?P<id>[a-z0-9]{24})/acknowledge/", method=["POST"],
          api=True, access="acknowledge")
    def api_acknowledge(self, request, id):
        alarm = get_alarm(id)
        if not alarm:
            return self.response_not_found()
        if alarm.status != "A":
            return self.response_not_found()
        if alarm.ack_ts:
            return {
                "status": False,
                "message": "Already acknowledged by %s" % alarm.ack_user
            }
        alarm.acknowledge(request.user)
        return {
            "status": True
        }

    @view(url=r"^(?P<id>[a-z0-9]{24})/unacknowledge/", method=["POST"],
          api=True, access="acknowledge")
    def api_unacknowledge(self, request, id):
        alarm = get_alarm(id)
        if not alarm:
            return self.response_not_found()
        if alarm.status != "A":
            return self.response_not_found()
        if not alarm.ack_ts:
            return {
                "status": False,
                "message": "Already unacknowledged"
            }
        alarm.unacknowledge(request.user)
        return {
            "status": True
        }

    @view(url=r"^(?P<id>[a-z0-9]{24})/subscribe/", method=["POST"],
          api=True, access="launch")
    def api_subscribe(self, request, id):
        alarm = get_alarm(id)
        if not alarm:
            return self.response_not_found()
        if alarm.status == "A":
            alarm.subscribe(request.user)
            return self.get_alarm_subscribers(alarm)
        else:
            return []

    @view(url=r"^(?P<id>[a-z0-9]{24})/unsubscribe/", method=["POST"],
          api=True, access="launch")
    def api_unsubscribe(self, request, id):
        alarm = get_alarm(id)
        if not alarm:
            return self.response_not_found()
        if alarm.status == "A":
            alarm.unsubscribe(request.user)
            return self.get_alarm_subscribers(alarm)
        else:
            return []

    @view(url=r"^(?P<id>[a-z0-9]{24})/clear/", method=["POST"],
          api=True, access="launch")
    def api_clear(self, request, id):
        alarm = get_alarm(id)
        if alarm.status == "A":
            alarm.clear_alarm("Cleared by %s" % request.user)
        return True

    @view(url=r"^(?P<id>[a-z0-9]{24})/set_root/", method=["POST"],
          api=True, access="launch",
          validate={"root": StringParameter()})
    def api_set_root(self, request, id, root):
        alarm = get_alarm(id)
        r = get_alarm(root)
        if not r:
            return self.response_not_found()
        alarm.set_root(r)
        return True

    @view(url="notification/$", method=["GET"],
          api=True, access="launch")
    def api_notification(self, request):
        delta = request.GET.get("delta")
        n = 0
        sound = None
        volume = 0
        if delta:
            dt = datetime.timedelta(seconds=int(delta))
            t0 = datetime.datetime.now() - dt
            r = list(ActiveAlarm._get_collection().aggregate([
                {
                    "$match": {
                        "timestamp": {
                            "$gt": t0
                        }
                    }
                },
                {
                    "$group": {
                        "_id": "$item",
                        "severity": {
                            "$max": "$severity"
                        }
                    }
                }
            ]))
            if r:
                s = AlarmSeverity.get_severity(r[0]["severity"])
                if s and s.sound and s.volume:
                    sound = "/ui/pkg/nocsound/%s.mp3" % s.sound
                    volume = float(s.volume) / 100.0
        return {
            "new_alarms": n,
            "sound": sound,
            "volume": volume
        }

    @classmethod
    def f_glyph_summary(cls, s, collapse=False):
        def be_true(p):
            return True

        def be_show(p):
            return p.show_in_summary

        def get_summary(d, profile):
            v = []
            if hasattr(profile, "show_in_summary"):
                show_in_summary = be_show
            else:
                show_in_summary = be_true
            for p, c in d.items():
                pv = profile.get_by_id(p)
                if pv and show_in_summary(pv):
                    if collapse and c < 2:
                        badge = ""
                    else:
                        badge = "<span class=\"x-display-tag\">%s</span>" % c
                    order = getattr(pv, "display_order", 100)
                    v += [(
                        (order, -c),
                        "<i class=\"%s\" title=\"%s\"></i>%s" % (
                            pv.glyph,
                            pv.name,
                            badge
                        )
                    )]
            return "<span class='x-summary'>%s</span>" % "".join(
                i[1] for i in sorted(v, key=operator.itemgetter(0))
            )

        if not isinstance(s, dict):
            return ""
        r = []
        if "subscriber" in s:
            from noc.crm.models.subscriberprofile import SubscriberProfile
            r += [get_summary(s["subscriber"], SubscriberProfile)]
        if "service" in s:
            from noc.sa.models.serviceprofile import ServiceProfile
            r += [get_summary(s["service"], ServiceProfile)]
        r = [x for x in r if x]
        return "".join(r)

    @view(url=r"^(?P<id>[a-z0-9]{24})/escalate/", method=["GET"],
          api=True, access="escalate")
    def api_escalation_alarm(self, request, id):
        alarm = get_alarm(id)
        if alarm.status == "A":
            AlarmEscalation.watch_escalations(alarm)
            return {'status': True}
        else:
            return {'status': False, 'error': 'The alarm is not active at the moment'}

    def location(self, id):
        """
        Return geo address for Managed Objects
        """

        def chunkIt(seq, num):
            avg = len(seq) / float(num)
            out = []
            last = 0.0

            while last < len(seq):
                out.append(seq[int(last):int(last + avg)])
                last += avg
            return out

        location = []
        address = Object.get_by_id(id).get_address_text()
        if address:
            for res in address.split(","):
                adr = normalize_division(res.strip().decode("utf-8").lower())
                if None in adr and "" in adr:
                    continue
                if None in adr:
                    location += [adr[1].title().strip()]
                else:
                    location += [' '.join(adr).title().strip()]
            res = chunkIt(location, 2)
            location_1 = ", ".join(res[0])
            location_2 = ", ".join(res[1])
            return [location_1, location_2]
        else:
            return ["", ""]

    @classmethod
    def f_summary(cls, s):
        def be_true(p):
            return True

        def be_show(p):
            return p.show_in_summary

        def get_summary(d, profile):
            v = []
            if hasattr(profile, "show_in_summary"):
                show_in_summary = be_show
            else:
                show_in_summary = be_true
            for p, c in sorted(d.items(), key=lambda x: -x[1]):
                pv = profile.get_by_id(p)
                if pv and show_in_summary(pv):
                    v += [{"profile": str(pv.id),
                           "glyph": pv.glyph,
                           "display_order": pv.display_order,
                           "profile__label": pv.name,
                           "summary": c}
                          ]
            return v

        if not isinstance(s, dict):
            return ""
        r = []
        if "subscriber" in s:
            from noc.crm.models.subscriberprofile import SubscriberProfile
            r += get_summary(s["subscriber"], SubscriberProfile)
        if "service" in s:
            from noc.sa.models.serviceprofile import ServiceProfile
            r += get_summary(s["service"], ServiceProfile)
        r = [x for x in r if x]
        return r

    @view(url=r"profile_lookup/$", access="launch", method=["GET"], api=True)
    def api_profile_lookup(self, request):
        from noc.crm.models.subscriberprofile import SubscriberProfile
        from noc.sa.models.serviceprofile import ServiceProfile
        r = []
        for model, short_type in ((ServiceProfile, _("Service")), (SubscriberProfile, _("Subscribers"))):
            r += [{"id": str(o.id), "type": short_type, "display_order": o.display_order,
                   "icon": o.glyph, "label": o.name}
                  for o in model.objects.all()
                  if getattr(o, "show_in_summary", True)]
        return r
