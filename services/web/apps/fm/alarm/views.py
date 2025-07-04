# ---------------------------------------------------------------------
# fm.alarm application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
import inspect
import datetime
import operator
from typing import Tuple, List, Dict, Any

# Third-party modules
import bson
import orjson
from pymongo import ReadPreference
from mongoengine.errors import DoesNotExist
from mongoengine.queryset.visitor import Q

# NOC modules
from noc.config import config
from noc.core.clickhouse.connect import connection
from noc.core.comp import smart_text
from noc.services.web.base.extapplication import ExtApplication, view
from noc.inv.models.object import Object
from noc.inv.models.networksegment import NetworkSegment
from noc.fm.models.activealarm import ActiveAlarm, Effect
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.fm.models.alarmclass import AlarmClass
from noc.fm.models.alarmseverity import AlarmSeverity
from noc.fm.models.activeevent import ActiveEvent
from noc.fm.models.archivedevent import ArchivedEvent
from noc.fm.models.eventclass import EventClass
from noc.fm.models.utils import get_alarm
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.resourcegroup import ResourceGroup
from noc.gis.utils.addr.ru import normalize_division
from noc.aaa.models.user import User
from noc.sa.models.useraccess import UserAccess
from noc.main.models.favorites import Favorites
from noc.sa.interfaces.base import (
    ModelParameter,
    UnicodeParameter,
    DateTimeParameter,
    StringParameter,
    StringListParameter,
    BooleanParameter,
    ListOfParameter,
    ObjectIdParameter,
)
from noc.maintenance.models.maintenance import Maintenance
from noc.crm.models.subscriberprofile import SubscriberProfile
from noc.sa.models.serviceprofile import ServiceProfile
from noc.sa.models.servicesummary import SummaryItem
from noc.fm.models.alarmplugin import AlarmPlugin
from noc.core.translation import ugettext as _
from noc.fm.models.alarmescalation import AlarmEscalation

SQL_EVENTS = f"""select
    e.event_id, e.ts,
    e.event_class as event_class_bi_id, e.managed_object as managed_object_bi_id,
    e.start_ts, e.source, e.raw_vars, e.resolved_vars, e.vars
    from events e
    where e.event_id in (select event_id from {config.clickhouse.db}.disposelog where alarm_id=%s)
    format JSONEachRow
"""


def get_advanced_field(id):
    if "|" in id:
        return id.split("|")
    for model, field in (
        (ServiceProfile, "total_services"),
        (SubscriberProfile, "total_subscribers"),
    ):
        if model.get_by_id(id):
            return field, id
    return "total_services"


class AlarmApplication(ExtApplication):
    """
    fm.alarm application
    """

    title = _("Alarm")
    menu = _("Alarms")
    glyph = "exclamation-triangle"

    implied_permissions = {"launch": ["sa:managedobject:alarm"]}

    model_map = {"A": ActiveAlarm, "C": ArchivedAlarm}

    clean_fields = {
        "managed_object": ModelParameter(ManagedObject),
        "timestamp": DateTimeParameter(),
    }

    ignored_params = ["status", "_dc"]

    diagnostic_plugin = AlarmPlugin(name="diagnostic", config={})

    advanced_filter_params = {
        "service_profile": "total_services",
        "subscribers_profile": "total_subscribers",
        "profile": get_advanced_field,
    }

    DEFAULT_ARCH_ALARM = datetime.timedelta(seconds=config.web.api_arch_alarm_limit)

    def __init__(self, *args, **kwargs):
        ExtApplication.__init__(self, *args, **kwargs)
        from .plugins.base import AlarmPlugin

        # Load plugins
        self.plugins = {}
        for f in os.listdir("services/web/apps/fm/alarm/plugins/"):
            if not f.endswith(".py") or f == "base.py" or f.startswith("_"):
                continue
            mn = "noc.services.web.apps.fm.alarm.plugins.%s" % f[:-3]
            m = __import__(mn, {}, {}, "*")
            for on in dir(m):
                o = getattr(m, on)
                if (
                    inspect.isclass(o)
                    and issubclass(o, AlarmPlugin)
                    and o.__module__.startswith(mn)
                ):
                    assert o.name
                    self.plugins[o.name] = o(self)

    def cleaned_query(self, q):
        q = q.copy()
        status = q["status"] if "status" in q else "A"
        for p in self.ignored_params:
            if p in q:
                del q[p]
        for p in (
            self.limit_param,
            self.page_param,
            self.start_param,
            self.format_param,
            self.sort_param,
            self.query_param,
            self.only_param,
        ):
            if p in q:
                del q[p]
        # Extract IN
        # extjs not working with same parameter name in query
        for p in list(q):
            if p.endswith("__in") and self.rx_oper_splitter.match(p):
                field = self.rx_oper_splitter.match(p).group("field") + "__in"
                if field not in q:
                    q[field] = [q[p]]
                else:
                    q[field] += [q[p]]
                del q[p]
        # Normalize parameters
        for p in list(q):
            qp = p.split("__")[0]
            if qp in self.clean_fields:
                q[p] = self.clean_fields[qp].clean(q[p])
        # Advanced filter
        for p in self.advanced_filter_params:
            params = []
            for x in list(q):
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
        # Grouped Alarms
        if "alarm_group" not in q:
            # Show all alarm
            q["alarm_group"] = "show"
        if q["alarm_group"] == "only" and status == "A":
            # Show Only Alarm without group
            q["groups"] = []
        del q["alarm_group"]
        # Exclude maintenance
        if "maintenance" not in q:
            q["maintenance"] = "hide"
        if q["maintenance"] == "hide" and status == "A":
            q["managed_object__nin"] = Maintenance.currently_affected()
        elif q["maintenance"] == "only" and status == "A":
            q["managed_object__in"] = Maintenance.currently_affected()
        del q["maintenance"]
        if "administrative_domain" in q:
            if q["administrative_domain"] != "_root_":
                q["adm_path"] = int(q["administrative_domain"])
            q.pop("administrative_domain")
        if "administrative_domain__in" in q:
            if "_root_" not in q["administrative_domain__in"]:
                q["adm_path__in"] = q["administrative_domain__in"]
            q.pop("administrative_domain__in")
        if "segment" in q:
            if q["segment"] != "_root_":
                q["segment_path"] = bson.ObjectId(q["segment"])
            q.pop("segment")
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
            q.pop("resource_group")
        if "cleared_after" in q:
            if status == "C":
                ca = int(q["cleared_after"])
                if ca:
                    q["clear_timestamp__gte"] = datetime.datetime.now() - datetime.timedelta(
                        seconds=ca
                    )
            q.pop("cleared_after")
        #
        if "wait_tt" in q:
            if status == "A":
                q["wait_tt__exists"] = True
                q["wait_ts__exists"] = False
            del q["wait_tt"]
        #
        if "collapse" in q:
            c = q["collapse"]
            del q["collapse"]
            if c != "0":
                q["root__exists"] = False
        #
        if "ephemeral" in q:
            c = q["ephemeral"]
            del q["ephemeral"]
            if c != "1":
                q["alarm_class__nin"] = list(
                    AlarmClass.objects.filter(is_ephemeral=True).values_list("id")
                )
        if status == "C":
            if (
                "timestamp__gte" not in q
                and "timestamp__lte" not in q
                and "clear_timestamp__gte" not in q
                and "clear_timestamp__lte" not in q
                and "escalation_tt__contains" not in q
                and "managed_object" not in q
            ):
                q["clear_timestamp__gte"] = datetime.datetime.now() - self.DEFAULT_ARCH_ALARM
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
                if callable(field):
                    field, c_id = field(c_id)
                c_id = bson.ObjectId(c_id)
            except bson.errors.InvalidId as e:
                self.logger.warning(e)
                continue
            if "~" in c_query:
                l, r = c_query.split("~")
                if not l:
                    cond = {"$lte": int(r)}
                elif not r:
                    cond = {"$gte": int(l)}
                else:
                    cond = {"$lte": int(r), "$gte": int(l)}
                q["__raw__"] = {field: {"$elemMatch": {"profile": c_id, "summary": cond}}}
            elif c_query == "exists":
                c_in += [c_id]
                continue
            elif c_query == "nexists":
                c_nin += [c_id]
                continue
            else:
                try:
                    c_query = int(c_query)
                    q["__raw__"] = {
                        field: {"$elemMatch": {"profile": c_id, "summary": int(c_query)}}
                    }
                except ValueError:
                    q["__raw__"] = {
                        field: {"$elemMatch": {"profile": c_id, "summary": {"$regex": c_query}}}
                    }
        if c_in:
            q["%s__profile__in" % field] = c_in
        if c_nin:
            q["%s__profile__nin" % field] = c_nin

        return q

    def instance_to_dict(self, o, fields=None):
        s = AlarmSeverity.get_severity(o.severity)
        n_events = (
            ActiveEvent.objects.filter(alarms=o.id).count()
            + ArchivedEvent.objects.filter(alarms=o.id).count()
        )
        location1, location2 = "", ""
        if o.managed_object and o.managed_object.container:
            location1, location2 = self.location(o.managed_object.container)
        d = {
            "id": str(o.id),
            "status": o.status,
            "managed_object": None,
            "managed_object__label": "",
            "administrative_domain": None,
            "administrative_domain__label": "",
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
            "segment__label": "",
            "segment": None,
            "location_1": location1,
            "location_2": location2,
            "escalation_tt": o.escalation_tt,
            "escalation_error": o.escalation_error,
            "platform": "",
            "address": "",
            "ack_ts": self.to_json(o.ack_ts),
            "ack_user": o.ack_user,
            "summary": self.f_glyph_summary(
                {
                    "subscriber": SummaryItem.items_to_dict(o.total_subscribers),
                    "service": SummaryItem.items_to_dict(o.total_services),
                }
            ),
            "total_objects": sum(x.summary for x in o.total_objects),
            "total_subscribers": self.f_summary(
                {"subscriber": SummaryItem.items_to_dict(o.total_subscribers)}
            ),
            "total_services": self.f_summary(
                {"service": SummaryItem.items_to_dict(o.total_services)}
            ),
            "logs": [
                {
                    "timestamp": self.to_json(ll.timestamp),
                    "user": ll.source or "NOC",
                    "message": ll.message,
                }
                for ll in o.log
                if getattr(ll, "source", None)
            ][: config.web.api_alarm_comments_limit],
        }
        if o.managed_object:
            d |= {
                "managed_object": o.managed_object.id,
                "managed_object__label": o.managed_object.name,
                "administrative_domain": o.managed_object.administrative_domain_id,
                "administrative_domain__label": o.managed_object.administrative_domain.name,
                "segment__label": o.managed_object.segment.name,
                "segment": str(o.managed_object.segment.id),
                "platform": o.managed_object.platform.name if o.managed_object.platform else "",
                "address": o.managed_object.address,
            }
        if fields:
            d = {k: d[k] for k in fields}
        return d

    def instance_to_dict_list(self, o, fields=None):
        r = self.instance_to_dict(o, fields)
        if fields:
            return r
        # Will be removed by bulk_field_group_subject
        r["__tmp_groups"] = o.groups[0] if o.groups else None
        return r

    def get_request_status(self, request) -> str:
        status = "A"
        ctype = request.META.get("CONTENT_TYPE")
        if request.GET and "status" in request.GET:
            status = request.GET.get("status", "A")
        elif request.POST and "status" in request.POST:
            # Form Data
            status = request.POST.get("status", "A")
        elif request.body and ctype and self.site.is_json(ctype):
            # Request data in body
            status = orjson.loads(request.body).get("status", "A")
        return status

    def queryset(self, request, query=None):
        """
        Filter records for lookup
        """
        status = self.get_request_status(request)
        if status not in self.model_map:
            raise Exception("Invalid status")
        model = self.model_map[status]
        if request.user.is_superuser:
            return model.objects.filter().read_preference(ReadPreference.SECONDARY_PREFERRED).all()
        return model.objects.filter(
            adm_path__in=UserAccess.get_domains(request.user),
        ).read_preference(ReadPreference.SECONDARY_PREFERRED)

    @view(method=["GET", "POST"], url=r"^$", access="launch", api=True)
    def api_list(self, request):
        return self.list_data(request, self.instance_to_dict)

    @view(url=r"^(?P<id>[a-z0-9]{24})/$", method=["GET"], api=True, access="launch")
    def api_alarm(self, request, id):
        alarm = get_alarm(id)
        if not alarm:
            self.response_not_found()
        user = request.user
        d = self.instance_to_dict(alarm)
        # Favorite status
        d["fav_status"] = str(alarm.id) in self.get_favorite_items(user)
        # Explanations
        d["body"] = alarm.body
        d["symptoms"] = alarm.alarm_class.symptoms
        d["probable_causes"] = alarm.alarm_class.probable_causes
        d["recommended_actions"] = alarm.alarm_class.recommended_actions
        d["vars"] = sorted(alarm.vars.items())
        d["status"] = alarm.status
        d["status__label"] = {"A": "Active", "C": "Cleared"}[alarm.status]
        # Managed object properties
        mo = alarm.managed_object
        if mo:
            d |= {
                "managed_object_address": mo.address,
                "managed_object_profile": mo.profile.name,
                "managed_object_platform": mo.platform.name if mo.platform else "",
                "managed_object_version": mo.version.version if mo.version else "",
                "segment": mo.segment.name,
                "segment_id": str(mo.segment.id),
                "segment_path": " | ".join(
                    NetworkSegment.get_by_id(p).name for p in NetworkSegment.get_path(mo.segment)
                ),
                "tags": mo.labels,
            }
        else:
            d |= {
                "managed_object_address": "",
                "managed_object_profile": "",
                "managed_object_platform": "",
                "managed_object_version": "",
                "segment": "",
                "segment_id": "",
                "segment_path": "",
                "tags": [],
            }
        if mo and mo.container:
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
            location = self.location(mo.container)
            if not location[0]:
                d["address_path"] = None
            else:
                d["address_path"] = ", ".join(location)
        # Log
        if alarm.log:
            d["log"] = [
                {
                    "timestamp": self.to_json(ll.timestamp),
                    "from_status": ll.from_status,
                    "to_status": ll.to_status,
                    "source": getattr(ll, "source", ""),
                    "message": ll.message,
                }
                for ll in alarm.log
            ]
        # Events
        events = []
        cursor = connection()
        res = cursor.execute(SQL_EVENTS, return_raw=True, args=[str(alarm.id)]).decode().split("\n")
        res = [orjson.loads(r) for r in res if r]
        for r in res:
            event = ActiveEvent(
                id=r["event_id"],
                timestamp=r["ts"],
                managed_object=ManagedObject.get_by_bi_id(r["managed_object_bi_id"]),
                event_class=EventClass.get_by_bi_id(r["event_class_bi_id"]),
                start_timestamp=r["start_ts"],
                source=r["source"],
                raw_vars=r["raw_vars"],
                resolved_vars=r["resolved_vars"],
                vars=r["vars"],
            )
            events += [
                {
                    "id": str(event.id),
                    "event_class": str(event.event_class.id),
                    "event_class__label": event.event_class.name,
                    "timestamp": event.timestamp,
                    "status": event.status,
                    "managed_object": event.managed_object.id,
                    "managed_object__label": event.managed_object.name,
                    "subject": event.subject,
                }
            ]
        if events:
            d["events"] = events
        # Alarms
        children = self.get_nested_alarms(alarm)
        if children:
            d["alarms"] = {"expanded": True, "children": children}
        # Subscribers
        if alarm.status == "A":
            d["subscribers"] = self.get_alarm_subscribers(alarm)
            d["is_subscribed"] = self.has_alarm_ubscriber(alarm, user)
        # Groups
        if alarm.groups:
            d["groups"] = []
            for ag in ActiveAlarm.objects.filter(reference__in=alarm.groups):
                d["groups"] += [
                    {
                        "id": str(ag.id),
                        "alarm_class": str(ag.alarm_class.id),
                        "alarm_class__label": ag.alarm_class.name,
                        "timestamp": self.to_json(ag.timestamp),
                        "subject": ag.subject,
                    }
                ]
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
        if "reference" in d:
            del d["reference"]
        return d

    def has_alarm_ubscriber(self, alarm: "ActiveAlarm", user: User) -> bool:
        """Check user subscription in alarm"""
        for w in alarm.watchers:
            if w.effect == Effect.SUBSCRIPTION and w.key == str(user.id):
                return True
        return False

    def get_alarm_subscribers(self, alarm: "ActiveAlarm"):
        """JSON-serializable subscribers"""
        subscribers = []
        for w in alarm.watchers:
            if w.effect != Effect.SUBSCRIPTION:
                continue
            try:
                u = User.get_by_id(int(w.key))
                subscribers += [
                    {"id": u.id, "name": " ".join([u.first_name, u.last_name]), "login": u.username}
                ]
            except User.DoesNotExist:
                pass
        return subscribers

    def get_nested_alarms(self, alarm, include_groups=True):
        """
        Return nested alarms as a part of NodeInterface
        :param alarm:
        :param include_groups
        :return:
        """
        children = []
        processed = set()
        for ac in (ActiveAlarm, ArchivedAlarm):
            for a_type, query in [
                ("nested", Q(root=alarm.id)),
                ("groups", Q(groups__in=[alarm.reference])),
            ]:
                if a_type == "groups" and (
                    (not include_groups or ac is ArchivedAlarm) or not alarm.reference
                ):
                    continue
                for a in ac.objects.filter(query):
                    if str(a.id) in processed:
                        # Already processed
                        continue
                    s = AlarmSeverity.get_severity(a.severity)
                    c = {
                        "id": str(a.id),
                        "subject": a.subject,
                        "alarm_class": str(a.alarm_class.id),
                        "alarm_class__label": a.alarm_class.name,
                        "managed_object": a.managed_object.id,
                        "managed_object__label": a.managed_object.name,
                        "timestamp": self.to_json(a.timestamp),
                        "groups": (
                            ", ".join(
                                ag.alarm_class.name
                                for ag in ActiveAlarm.objects.filter(reference__in=a.groups)
                            )
                            if a.groups
                            else ""
                        ),
                        "iconCls": "icon_error",
                        "row_class": s.style.css_class_name,
                    }
                    nc = self.get_nested_alarms(a, include_groups=False)
                    if nc:
                        c["children"] = nc
                        c["expanded"] = True
                    else:
                        c["leaf"] = True
                    children.append(c)
                    processed.add(c["id"])
        return children

    @view(
        url=r"^(?P<id>[a-z0-9]{24})/post/",
        method=["POST"],
        api=True,
        access="launch",
        validate={"msg": UnicodeParameter()},
    )
    def api_post(self, request, id, msg):
        alarm = get_alarm(id)
        if not alarm:
            self.response_not_found()
        alarm.log_message(msg, source=request.user.username)
        return True

    @view(
        url=r"^comment/post/",
        method=["POST"],
        api=True,
        access="launch",
        validate={
            "ids": StringListParameter(required=True),
            "msg": UnicodeParameter(),
        },
    )
    def api_comment_post(self, request, ids, msg):
        alarms = list(ActiveAlarm.objects.filter(id__in=ids))
        alarms += list(ArchivedAlarm.objects.filter(id__in=ids))
        if not alarms:
            self.response_not_found()
        for alarm in alarms:
            alarm.log_message(msg, source=request.user.username)
        return True

    @view(
        url=r"^group/favorites/",
        method=["POST"],
        api=True,
        access="launch",
        validate={
            "ids": StringListParameter(required=True),
            "fav_status": BooleanParameter(),
        },
    )
    def api_group_favorites(self, request, ids: list[str], fav_status: bool):
        if fav_status:
            Favorites.add_items(request.user, self.app_id, ids)
        else:
            Favorites.remove_items(request.user, self.app_id, ids)
        return {"status": True}

    @view(
        url=r"^(?P<id>[a-z0-9]{24})/acknowledge/",
        method=["POST"],
        api=True,
        access="acknowledge",
        validate={
            "msg": UnicodeParameter(default=""),
        },
    )
    def api_acknowledge(self, request, id, msg=""):
        alarm = get_alarm(id)
        if not alarm:
            return self.response_not_found()
        if alarm.status != "A":
            return self.response_not_found()
        if alarm.ack_ts:
            return {"status": False, "message": "Already acknowledged by %s" % alarm.ack_user}
        alarm.acknowledge(request.user, msg)
        return {"status": True}

    @view(
        url=r"^(?P<id>[a-z0-9]{24})/unacknowledge/",
        method=["POST"],
        api=True,
        access="acknowledge",
        validate={
            "msg": UnicodeParameter(default=""),
        },
    )
    def api_unacknowledge(self, request, id, msg=""):
        alarm = get_alarm(id)
        if not alarm:
            return self.response_not_found()
        if alarm.status != "A":
            return self.response_not_found()
        if not alarm.ack_ts:
            return {"status": False, "message": "Already unacknowledged"}
        alarm.unacknowledge(request.user, msg=msg)
        return {"status": True}

    @view(url=r"^(?P<id>[a-z0-9]{24})/subscribe/", method=["POST"], api=True, access="launch")
    def api_subscribe(self, request, id):
        alarm = get_alarm(id)
        if not alarm:
            return self.response_not_found()
        if alarm.status == "A":
            alarm.subscribe(request.user)
            return self.get_alarm_subscribers(alarm)
        return []

    @view(url=r"^(?P<id>[a-z0-9]{24})/unsubscribe/", method=["POST"], api=True, access="launch")
    def api_unsubscribe(self, request, id):
        alarm = get_alarm(id)
        if not alarm:
            return self.response_not_found()
        if alarm.status == "A":
            alarm.unsubscribe(request.user)
            return self.get_alarm_subscribers(alarm)
        return []

    @view(
        url=r"^(?P<id>[a-z0-9]{24})/clear/",
        method=["POST"],
        api=True,
        access="launch",
        validate={
            "msg": UnicodeParameter(default=""),
        },
    )
    def api_clear(self, request, id, msg=""):
        alarm = get_alarm(id)
        if not alarm.alarm_class.user_clearable:
            return {"status": False, "error": "Deny clear alarm by user"}
        if alarm.status == "A":
            # Send clear signal to the correlator
            alarm.register_clear(f"Cleared by user: {request.user.username}", user=request.user)
        return True

    @view(
        url=r"^clear/",
        method=["POST"],
        api=True,
        access="clear",
        validate={
            "msg": UnicodeParameter(default=""),
            "alarms": ListOfParameter(ObjectIdParameter()),
        },
    )
    def api_group_clear(self, request, msg: str, alarms: list[str]):
        success = 0
        failed = 0
        for alarm_id in alarms:
            alarm = get_alarm(alarm_id)
            if not alarm.alarm_class.user_clearable or alarm.status != "A":
                failed += 1
                continue
            alarm.register_clear(msg, user=request.user)
            success += 1
        if success:
            return {"status": True}
        return {"status": False, "message": _("Failed to clear alarms")}

    @view(
        url=r"^(?P<id>[a-z0-9]{24})/set_root/",
        method=["POST"],
        api=True,
        access="launch",
        validate={"root": StringParameter()},
    )
    def api_set_root(self, request, id, root):
        alarm = get_alarm(id)
        r = get_alarm(root)
        if not r:
            return self.response_not_found()
        alarm.set_root(r)
        return True

    @view(url=r"notification/$", method=["GET"], api=True, access="launch")
    def api_notification(self, request):
        delta = request.GET.get("delta")
        n = 0
        sound = None
        volume = 0
        if delta:
            dt = datetime.timedelta(seconds=int(delta))
            t0 = datetime.datetime.now() - dt
            r = list(
                ActiveAlarm._get_collection().aggregate(
                    [
                        {"$match": {"timestamp": {"$gt": t0}}},
                        {"$group": {"_id": "$item", "severity": {"$max": "$severity"}}},
                    ]
                )
            )
            if r:
                s = AlarmSeverity.get_severity(r[0]["severity"])
                if s and s.sound and s.volume:
                    sound = "/ui/pkg/nocsound/%s.mp3" % s.sound
                    volume = float(s.volume) / 100.0
        return {"new_alarms": n, "sound": sound, "volume": volume}

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
                        badge = '<span class="x-display-tag">%s</span>' % c
                    order = getattr(pv, "display_order", 100)
                    v += [
                        (
                            (order, -c),
                            '<i class="%s" title="%s"></i>%s' % (pv.glyph, pv.name, badge),
                        )
                    ]
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

    @view(
        url=r"^escalate/",
        method=["POST"],
        api=True,
        access="escalate",
        validate={"ids": StringListParameter(required=True)},
    )
    def api_escalation_alarm(self, request, ids):
        alarms = list(ActiveAlarm.objects.filter(id__in=ids))
        if not alarms:
            return self.response_not_found()
        for alarm in alarms:
            if alarm.alarm_class.is_ephemeral:
                # Ephemeral alarm has not escalated
                continue
            if alarm.escalation_tt:
                alarm.log_message(
                    "Already escalated with TT #%s" % alarm.escalation_tt,
                    source=request.user.username,
                )
            elif alarm.root:
                alarm.log_message(
                    "Alarm is not root cause, skipping escalation",
                    source=request.user.username,
                )
            else:
                alarm.log_message(
                    "Alarm has been escalated by %s" % request.user.username,
                    source=request.user.username,
                )
                AlarmEscalation.watch_escalations(alarm, force=True)
        return {"status": True}

    @staticmethod
    def location(oid: str) -> Tuple[str, str]:
        """
        Return geo address for Managed Objects
        """

        def chunk_it(seq, num):
            avg = len(seq) / float(num)
            out = []
            last = 0.0

            while last < len(seq):
                out.append(seq[int(last) : int(last + avg)])
                last += avg
            return out

        location = []
        if isinstance(oid, Object):
            o = oid
        else:
            o = Object.get_by_id(oid)
        if not o:
            return "", ""
        address = o.get_address_text()
        if address:
            for res in address.split(","):
                adr = normalize_division(smart_text(res).strip().lower())
                if None in adr and "" in adr:
                    continue
                if None in adr:
                    location += [adr[1].title().strip()]
                else:
                    location += [" ".join(adr).title().strip()]
            res = chunk_it(location, 2)
            return ", ".join(res[0]), ", ".join(res[1])
        return "", ""

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
                    v += [
                        {
                            "profile": str(pv.id),
                            "glyph": pv.glyph,
                            "display_order": pv.display_order,
                            "profile__label": pv.name,
                            "summary": c,
                        }
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

    def bulk_field_total_grouped(self, data):
        if not data or data[0]["status"] != "A":
            return data
        refs = [x["reference"] for x in data if "reference" in x]
        if not refs:
            return data
        coll = ActiveAlarm._get_collection()
        r = {
            c["_id"]: c["count"]
            for c in coll.aggregate(
                [
                    {"$match": {"groups": {"$in": refs}}},
                    {"$unwind": "$groups"},
                    {"$group": {"_id": "$groups", "count": {"$sum": 1}}},
                ]
            )
        }
        for x in data:
            if "reference" in x:
                x["total_grouped"] = r.get(x["reference"], 0)
                del x["reference"]
        return data

    def bulk_field_isinmaintenance(self, data):
        if not data:
            return data
        if data[0]["status"] == "A":
            mtc = set(Maintenance.currently_affected())
            for x in data:
                x["isInMaintenance"] = x["managed_object"] in mtc
        return data

    def bulk_field_group_subject(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not data or data[0]["status"] != "A":
            return data
        # Get existing refs
        group_refs = {x["__tmp_groups"] for x in data if "__tmp_groups" in x}
        if not group_refs:
            return data
        # Find subject
        subj_map = {}
        for x in ActiveAlarm._get_collection().find(
            {"reference": {"$in": list(group_refs)}}, {"_id": 1, "reference": 1, "vars": 1}
        ):
            av = x.get("vars")
            if not av:
                continue
            name = av.get("name")
            if name:
                subj_map[x["reference"]] = name
        # Apply subjects
        for x in data:
            g = x.pop("__tmp_groups", None)
            if not g or g not in subj_map:
                continue
            x["group_subject"] = subj_map[g]
        return data

    @view(url=r"profile_lookup/$", access="launch", method=["GET"], api=True)
    def api_profile_lookup(self, request):
        r = []
        for model, short_type, field_id in (
            (ServiceProfile, _("Service"), "total_services"),
            (SubscriberProfile, _("Subscribers"), "total_subscribers"),
        ):
            # "%s|%s" % (field_id,
            r += [
                {
                    "id": str(o.id),
                    "type": short_type,
                    "display_order": o.display_order,
                    "icon": o.glyph,
                    "label": o.name,
                }
                for o in model.objects.all()
                if getattr(o, "show_in_summary", True)
            ]
        return r
