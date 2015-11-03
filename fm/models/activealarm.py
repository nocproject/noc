# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ActiveAlarm model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## Django modules
from django.template import Template, Context
## NOC modules
import noc.lib.nosql as nosql
from alarmlog import AlarmLog
from alarmclass import AlarmClass
from noc.main.models import User
from noc.main.models.style import Style
from noc.main.models.notification import Notification
from noc.sa.models.managedobject import ManagedObject
from alarmseverity import AlarmSeverity


class ActiveAlarm(nosql.Document):
    meta = {
        "collection": "noc.alarms.active",
        "allow_inheritance": False,
        "indexes": [
            "timestamp", "discriminator", "root", "-severity",
            "alarm_class",
            ("timestamp", "managed_object")
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

    def __unicode__(self):
        return u"%s" % self.id

    def save(self, *args, **kwargs):
        if not self.last_update:
            self.last_update = self.timestamp
        return super(ActiveAlarm, self).save(*args, **kwargs)

    def _change_root_severity(self):
        """
        Change root severity, when necessary
        """
        if not self.root:
            return
        root = get_alarm(self.root)
        if root and root.severity < self.severity:
            root.change_severity(self.severity)
            root.log_message(
                "Severity has been increased by child alarm %s" % self.id
            )

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
            self.severity = severity.severity
            self.log_message(
                "%s has changed severity to %s" % (user, severity.name))
        self._change_root_severity()
        self.save()

    def log_message(self, message, to_save=True):
        self.log += [AlarmLog(timestamp=datetime.datetime.now(),
                     from_status=self.status, to_status=self.status,
                     message=message)]
        if to_save:
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
        self.save()
        # Update event's list of alarms
        if self.id not in e.alarms:
            e.alarms.append(self.id)
            e.expires = None
            e.save()

    def clear_alarm(self, message):
        ts = datetime.datetime.now()
        log = self.log + [AlarmLog(timestamp=ts, from_status="A",
                                   to_status="C", message=message)]
        a = ArchivedAlarm(id=self.id,
                          timestamp=self.timestamp,
                          clear_timestamp=ts,
                          managed_object=self.managed_object,
                          alarm_class=self.alarm_class,
                          severity=self.severity,
                          vars=self.vars,
                          log=log,
                          root=self.root,
                          opening_event=self.opening_event,
                          closing_event=self.closing_event,
                          discriminator=self.discriminator,
                          reopens=self.reopens
                          )
        ct = self.alarm_class.get_control_time(self.reopens)
        if ct:
            a.control_time = datetime.datetime.now() + datetime.timedelta(seconds=ct)
        a.save()
        # @todo: Clear related correlator jobs
        self.delete()
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
            # Schedule delayed job
            #submit_job("fm.correlator", "control_notify",
            #           key=a.id, ts=a.control_time)
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
        s = Template(self.alarm_class.subject_template).render(ctx)
        if len(s) >= 255:
            s = s[:125] + " ... " + s[-125:]
        return s

    @property
    def body(self):
        ctx = Context(self.get_template_vars())
        s = Template(self.alarm_class.body_template).render(ctx)
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
        self._change_root_severity()
        # Clear pending notifications
        Notification.purge_delayed("alarm:%s" % self.id)

    @classmethod
    def enable_caching(cls, ttl=600):
        cls._fields["alarm_class"].set_cache(ttl)

## Avoid circular references
from archivedalarm import ArchivedAlarm
from utils import get_alarm
