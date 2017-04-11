# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ActiveAlarm model
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## Django modules
from django.template import Template as DjangoTemplate
from django.template import Context
## NOC modules
import noc.lib.nosql as nosql
from alarmlog import AlarmLog
from alarmclass import AlarmClass
from noc.main.models import User
from noc.main.models.style import Style
from noc.main.models.notificationgroup import NotificationGroup
from noc.main.models.template import Template
from noc.sa.models.managedobject import ManagedObject
from alarmseverity import AlarmSeverity
from noc.sa.models.servicesummary import ServiceSummary, SummaryItem, ObjectSummaryItem
from noc.core.defer import call_later
from noc.lib.debug import error_report


class ActiveAlarm(nosql.Document):
    meta = {
        "collection": "noc.alarms.active",
        "allow_inheritance": False,
        "indexes": [
            "timestamp", "root", "-severity",
            ("alarm_class", "managed_object"),
            ("discriminator", "managed_object"),
            ("timestamp", "managed_object"),
            "escalation_tt",
            "escalation_ts",
            "adm_path",
            "segment_path",
            "container_path",
            "uplinks"
        ]
    }
    status = "A"

    timestamp = nosql.DateTimeField(required=True)
    last_update = nosql.DateTimeField(required=True)
    managed_object = nosql.ForeignKeyField(ManagedObject)
    alarm_class = nosql.PlainReferenceField(AlarmClass)
    severity = nosql.IntField(required=True)
    vars = nosql.DictField()
    # Calculated alarm discriminator
    # Has meaning only for alarms with is_unique flag set
    # Calculated as sha1("value1\x00....\x00valueN").hexdigest()
    discriminator = nosql.StringField(required=False)
    log = nosql.ListField(nosql.EmbeddedDocumentField(AlarmLog))
    # Responsible person
    owner = nosql.ForeignKeyField(User, required=False)
    #
    opening_event = nosql.ObjectIdField(required=False)
    closing_event = nosql.ObjectIdField(required=False)
    # List of subscribers
    subscribers = nosql.ListField(nosql.ForeignKeyField(User))
    #
    custom_subject = nosql.StringField(required=False)
    custom_style = nosql.ForeignKeyField(Style, required=False)
    #
    reopens = nosql.IntField(required=False)
    # RCA
    # Reference to root cause (Active Alarm or Archived Alarm instance)
    root = nosql.ObjectIdField(required=False)
    # Escalated TT ID in form
    # <external system name>:<external tt id>
    escalation_ts = nosql.DateTimeField(required=False)
    escalation_tt = nosql.StringField(required=False)
    escalation_error = nosql.StringField(required=False)
    # Close tt when alarm cleared
    close_tt = nosql.BooleanField(default=False)
    # Do not clear alarm until *wait_tt* is closed
    wait_tt = nosql.StringField()
    wait_ts = nosql.DateTimeField()
    # Directly affected services summary, grouped by profiles
    # (connected to the same managed object)
    direct_services = nosql.ListField(nosql.EmbeddedDocumentField(SummaryItem))
    direct_subscribers = nosql.ListField(nosql.EmbeddedDocumentField(SummaryItem))
    # Indirectly affected services summary, groupped by profiles
    # (covered by this and all inferred alarms)
    total_objects = nosql.ListField(nosql.EmbeddedDocumentField(ObjectSummaryItem))
    total_services = nosql.ListField(nosql.EmbeddedDocumentField(SummaryItem))
    total_subscribers = nosql.ListField(nosql.EmbeddedDocumentField(SummaryItem))
    # Template and notification group to send close notification
    clear_template = nosql.ForeignKeyField(Template, required=False)
    clear_notification_group = nosql.ForeignKeyField(NotificationGroup, required=False)
    # Paths
    adm_path = nosql.ListField(nosql.IntField())
    segment_path = nosql.ListField(nosql.ObjectIdField())
    container_path = nosql.ListField(nosql.ObjectIdField())
    # Uplinks, for topology_rca only
    uplinks = nosql.ListField(nosql.IntField())

    def __unicode__(self):
        return u"%s" % self.id

    def save(self, *args, **kwargs):
        if not self.last_update:
            self.last_update = self.timestamp
        data = self.managed_object.data
        self.adm_path = data.adm_path
        self.segment_path = data.segment_path
        self.container_path = data.container_path
        self.uplinks = data.uplinks
        return super(ActiveAlarm, self).save(*args, **kwargs)

    def change_severity(self, user="", delta=None, severity=None):
        """
        Change alarm severity
        """
        if isinstance(user, User):
            user = user.username
        if delta:
            self.severity = max(0, self.severity + delta)
            if delta > 0:
                self.log_message(
                    "%s has increased alarm severity by %s" % (
                        user, delta))
            else:
                self.log_message(
                    "%s has decreased alarm severity by %s" % (
                        user, delta))
        elif severity:
            if type(severity) in (int, long, float):
                self.severity = int(severity)
                self.log_message(
                    "%s has changed severity to %s" % (user, severity))
            else:
                self.severity = severity.severity
                self.log_message(
                    "%s has changed severity to %s" % (user, severity.name))
        if self.id:
            self.save(save_condition={"id": self.id})
        else:
            self.save()

    def log_message(self, message, to_save=True):
        self.log += [AlarmLog(timestamp=datetime.datetime.now(),
                     from_status=self.status, to_status=self.status,
                     message=message)]
        if to_save:
            if self.id:
                self.save(save_condition={"id": self.id})
            else:
                self.save()

    def contribute_event(self, e, open=False, close=False):
        # Set opening event when necessary
        if open:
            self.opening_event = e.id
        # Set closing event when necessary
        if close:
            self.closing_event = e.id
        # Update timestamp
        if e.timestamp < self.timestamp:
            self.timestamp = e.timestamp
        else:
            self.last_update = max(self.last_update, e.timestamp)
        if self.id:
            self.save(save_condition={"id": self.id})
        else:
            self.save()
        # Update event's list of alarms
        if self.id not in e.alarms:
            e._get_collection().update({
                "_id": e.id,
            }, {
                "$set": {
                    "expires": None,
                },
                "$push": {
                    "alarms": self.id
                }
            })
            e.alarms.append(self.id)
            e.expires = None
            # e.save()

    def clear_alarm(self, message, ts=None, force=False):
        """
        Clear alarm
        :param message: Log clearing message
        :param ts: Clearing timestamp
        :param force: Clear ever if wait_tt seg
        """
        ts = ts or datetime.datetime.now()
        if self.wait_tt and not force:
            # Wait for escalated tt to close
            if not self.wait_ts:
                self.wait_ts = ts
                self.log_message("Waiting for TT to close")
                call_later(
                    "noc.services.escalator.wait_tt.wait_tt",
                    scheduler="escalator",
                    alarm_id=self.id
                )
            return
        if self.alarm_class.clear_handlers:
            # Process clear handlers
            for h in self.alarm_class.get_clear_handlers():
                try:
                    h(self)
                except:
                    error_report()
        log = self.log + [AlarmLog(timestamp=ts, from_status="A",
                                   to_status="C", message=message)]
        a = ArchivedAlarm(
            id=self.id,
            timestamp=self.timestamp,
            clear_timestamp=ts,
            managed_object=self.managed_object,
            alarm_class=self.alarm_class,
            severity=self.severity,
            vars=self.vars,
            log=log,
            root=self.root,
            escalation_ts=self.escalation_ts,
            escalation_tt=self.escalation_tt,
            escalation_error=self.escalation_error,
            opening_event=self.opening_event,
            closing_event=self.closing_event,
            discriminator=self.discriminator,
            reopens=self.reopens,
            direct_services=self.direct_services,
            direct_subscribers=self.direct_subscribers,
            total_objects=self.total_objects,
            total_services=self.total_services,
            total_subscribers=self.total_subscribers,
            adm_path=self.adm_path,
            segment_path=self.segment_path,
            container_path=self.container_path,
            uplinks=self.uplinks
        )
        ct = self.alarm_class.get_control_time(self.reopens)
        if ct:
            a.control_time = datetime.datetime.now() + datetime.timedelta(seconds=ct)
        a.save()
        # Send notifications
        if not a.root and not self.reopens:
            a.managed_object.event(a.managed_object.EV_ALARM_CLEARED, {
                "alarm": a,
                "subject": a.subject,
                "body": a.body,
                "symptoms": a.alarm_class.symptoms,
                "recommended_actions": a.alarm_class.recommended_actions,
                "probable_causes": a.alarm_class.probable_causes
            })
        elif ct:
            pass
        if a.escalation_tt or self.clear_template:
            if self.clear_template:
                ctx = {
                    "alarm": a
                }
                subject = self.clear_template.render_subject(**ctx)
                body = self.clear_template.render_body(**ctx)
            else:
                subject = "Alarm cleared"
                body = "Alarm has been cleared"
            call_later(
                "noc.services.escalator.escalation.notify_close",
                scheduler="escalator",
                alarm_id=self.id,
                tt_id=self.escalation_tt,
                subject=subject,
                body=body,
                notification_group_id=self.clear_notification_group.id if self.clear_notification_group else None,
                close_tt=self.close_tt
            )
        # Set checks on all consequences
        for d in self._get_collection().find({
            "root": self.id
        }, {"_id": 1, "alarm_class": 1}):
            ac = AlarmClass.get_by_id(d["alarm_class"])
            if not ac:
                continue
            t = ac.recover_time
            if not t:
                continue
            call_later(
                "noc.services.correlator.check.check_close_consequence",
                scheduler="correlator",
                pool=self.managed_object.pool.name,
                delay=t,
                alarm_id=d["_id"]
            )
        # Clear alarm
        self.delete()
        # Gather diagnostics
        AlarmDiagnosticConfig.on_clear(a)
        # Return archived
        return a

    def get_template_vars(self):
        """
        Prepare template variables
        """
        vars = self.vars.copy()
        vars.update({"alarm": self})
        return vars

    @property
    def subject(self):
        ctx = Context(self.get_template_vars())
        s = DjangoTemplate(self.alarm_class.subject_template).render(ctx)
        if len(s) >= 255:
            s = s[:125] + " ... " + s[-125:]
        return s

    @property
    def body(self):
        ctx = Context(self.get_template_vars())
        s = DjangoTemplate(self.alarm_class.body_template).render(ctx)
        return s

    def change_owner(self, user):
        """
        Change alarm's owner
        """
        self.owner = user
        self.save()

    def subscribe(self, user):
        """
        Change alarm's subscribers
        """
        if user.id not in self.subscribers:
            self.subscribers += [user.id]
            self.log_message("%s(%s) has been subscribed" % (
                (" ".join([user.first_name, user.last_name]),
                 user.username)
            ), to_save=False)
            self.save()

    def unsubscribe(self, user):
        if self.is_subscribed(user):
            self.subscribers = [u.id for u in self.subscribers
                                if u != user.id]
            self.log_message("%s(%s) has been unsubscribed" % (
                (" ".join([user.first_name, user.last_name]),
                 user.username)
            ), to_save=False)
            self.save()

    def is_owner(self, user):
        return self.owner == user

    def is_subscribed(self, user):
        return user.id in self.subscribers

    @property
    def is_unassigned(self):
        return self.owner is None

    @property
    def duration(self):
        dt = datetime.datetime.now() - self.timestamp
        return dt.days * 86400 + dt.seconds

    @property
    def display_duration(self):
        duration = datetime.datetime.now() - self.timestamp
        secs = duration.seconds % 60
        mins = (duration.seconds / 60) % 60
        hours = (duration.seconds / 3600) % 24
        days = duration.days
        r = "%02d:%02d:%02d" % (hours, mins, secs)
        if days:
            r = "%dd %s" % (days, r)
        return r

    @property
    def effective_style(self):
        if self.custom_style:
            return self.custom_style
        else:
            return AlarmSeverity.get_severity(self.severity).style

    def get_root(self):
        """
        Get top-level root alarm
        """
        root = self
        while root.root:
            root = get_alarm(root.root)
        return root

    def update_summary(self):
        def update_dict(d1, d2):
            for k in d2:
                if k in d1:
                    d1[k] += d2[k]
                else:
                    d1[k] = d2[k]

        services = SummaryItem.items_to_dict(self.direct_services)
        subscribers = SummaryItem.items_to_dict(self.direct_subscribers)
        objects = {
            self.managed_object.object_profile.id: 1
        }

        for a in ActiveAlarm.objects.filter(root=self.id):
            a.update_summary()
            update_dict(
                objects,
                SummaryItem.items_to_dict(a.total_objects)
            )
            update_dict(
                services,
                SummaryItem.items_to_dict(a.total_services)
            )
            update_dict(
                subscribers,
                SummaryItem.items_to_dict(a.total_subscribers)
            )
        obj_list = ObjectSummaryItem.dict_to_items(objects)
        svc_list = SummaryItem.dict_to_items(services)
        sub_list = SummaryItem.dict_to_items(subscribers)
        if svc_list != self.total_services or sub_list != self.total_subscribers or obj_list != self.total_objects:
            ns = ServiceSummary.get_severity({
                "service": services,
                "subscriber": subscribers,
                "objects": objects
            })
            self.total_objects = obj_list
            self.total_services = svc_list
            self.total_subscribers = sub_list
            if ns != self.severity:
                self.change_severity(severity=ns)
            self.save(save_condition={
                "id": self.id
            })

    def set_root(self, root_alarm):
        """
        Set root cause
        """
        if self.root:
            return
        if self.id == root_alarm.id:
            raise Exception("Cannot set self as root cause")
        # Detect loop
        root = root_alarm
        while root and root.root:
            root = root.root
            if root == self.id:
                return
            root = get_alarm(root)
        # Set root
        self.root = root_alarm.id
        self.log_message(
            "Alarm %s has been marked as root cause" % root_alarm.id)
        # self.save()  Saved by log_message
        root_alarm.log_message(
            "Alarm %s has been marked as child" % self.id)
        root_alarm.update_summary()
        # Clear pending notifications
        # Notification.purge_delayed("alarm:%s" % self.id)

    def escalate(self, tt_id, close_tt=False):
        self.escalation_tt = tt_id
        self.escalation_ts = datetime.datetime.now()
        self.close_tt = close_tt
        self.log_message("Escalated to %s" % tt_id)
        r = ActiveAlarm._get_collection().update({
            "_id": self.id
        }, {
            "$set": {
                "escalation_tt": self.escalation_tt,
                "escalation_ts": self.escalation_ts,
                "close_tt": self.close_tt
            }
        })
        if r.get("nModified", 0) == 0:
            # Already closed, update archive
            ArchivedAlarm._get_collection().update({
                "_id": self.id
            }, {
                "$set": {
                    "escalation_tt": self.escalation_tt,
                    "escalation_ts": self.escalation_ts,
                    "close_tt": self.close_tt
                }
            })
        # self.save(save_condition={
        #     "managed_object": {
        #         "$exists": True
        #     },
        #     "id": self.id
        # })

    def set_escalation_error(self, error):
        self.escalation_error = error
        self._get_collection().update(
            {"_id": self.id},
            {"$set": {
                "escalation_error": error
            }}
        )

    def set_clear_notification(self, notification_group, template):
        self.clear_notification_group = notification_group
        self.clear_template = template
        self.save(save_condition={
            "managed_object": {
                "$exists": True
            },
            "id": self.id
        })

    def iter_consequences(self):
        """
        Generator yielding all consequences alarm
        """
        for a in ActiveAlarm.objects.filter(root=self.id):
            yield a
            for ca in a.iter_consequences():
                yield ca

    def iter_affected(self):
        """
        Generator yielding all affected managed objects
        """
        seen = set([self.managed_object])
        yield self.managed_object
        for a in self.iter_consequences():
            if a.managed_object not in seen:
                seen.add(a.managed_object)
                yield a.managed_object

    def iter_escalated(self):
        """
        Generator yielding all escalated consequences
        """
        for a in self.iter_consequences():
            if a.escalation_tt:
                yield a

## Avoid circular references
from archivedalarm import ArchivedAlarm
from utils import get_alarm
from alarmdiagnosticconfig import AlarmDiagnosticConfig
