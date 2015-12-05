# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ArchivedAlarm model
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
from noc.sa.models.managedobject import ManagedObject
from alarmclass import AlarmClass
from alarmlog import AlarmLog
from alarmseverity import AlarmSeverity


class ArchivedAlarm(nosql.Document):
    meta = {
        "collection": "noc.alarms.archived",
        "allow_inheritance": False,
        "indexes": [
            "root",
            "control_time",
            "timestamp",
            "managed_object"
        ]
    }
    status = "C"

    timestamp = nosql.DateTimeField(required=True)
    clear_timestamp = nosql.DateTimeField(required=True)
    managed_object = nosql.ForeignKeyField(ManagedObject)
    alarm_class = nosql.PlainReferenceField(AlarmClass)
    severity = nosql.IntField(required=True)
    vars = nosql.DictField()
    log = nosql.ListField(nosql.EmbeddedDocumentField(AlarmLog))
    #
    opening_event = nosql.ObjectIdField(required=False)
    closing_event = nosql.ObjectIdField(required=False)
    # Number of reopens
    reopens = nosql.IntField(required=False)
    # Copied discriminator
    discriminator = nosql.StringField(required=False)
    # Control time within alarm will be reopen instead
    # instead of creating the new alarm
    control_time = nosql.DateTimeField(required=False)
    # RCA
    # Reference to root cause (Active Alarm or Archived Alarm instance)
    root = nosql.ObjectIdField(required=False)

    def __unicode__(self):
        return u"%s" % self.id

    def log_message(self, message):
        self.log += [AlarmLog(timestamp=datetime.datetime.now(),
                     from_status=self.status, to_status=self.status,
                     message=message)]
        self.save()

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

    @property
    def duration(self):
        dt = self.clear_timestamp - self.timestamp
        return dt.days * 86400 + dt.seconds

    @property
    def display_duration(self):
        duration = self.clear_timestamp - self.timestamp
        secs = duration.seconds % 60
        mins = (duration.seconds / 60) % 60
        hours = (duration.seconds / 3600) % 24
        days = duration.days
        if days:
            return "%dd %02d:%02d:%02d" % (days, hours, mins, secs)
        else:
            return "%02d:%02d:%02d" % (hours, mins, secs)

    @property
    def effective_style(self):
        return AlarmSeverity.get_severity(self.severity).style

    def set_root(self, root_alarm):
        pass

    def reopen(self, message):
        """
        Reopen alarm back
        """
        reopens = self.reopens or 0
        ts = datetime.datetime.now()
        log = self.log + [AlarmLog(timestamp=ts, from_status="C",
                                   to_status="A", message=message)]
        a = ActiveAlarm(
            id=self.id,
            timestamp=self.timestamp,
            last_update=ts,
            managed_object=self.managed_object,
            alarm_class=self.alarm_class,
            severity=self.severity,
            vars=self.vars,
            log=log,
            root=self.root,
            opening_event=self.opening_event,
            discriminator=self.discriminator,
            reopens=reopens + 1
        )
        a.save()
        # @todo: Clear related correlator jobs
        self.delete()
        # Remove pending control_notify job
        #remove_job("fm.correlator", "control_notify", key=a.id)
        # Send notifications
        # Do not set notifications for child and for previously reopened
        # alarms
        if not a.root and not reopens:
            a.managed_object.event(a.managed_object.EV_ALARM_REOPENED, {
                "alarm": a,
                "subject": a.subject,
                "body": a.body,
                "symptoms": a.alarm_class.symptoms,
                "recommended_actions": a.alarm_class.recommended_actions,
                "probable_causes": a.alarm_class.probable_causes
            })
        return a

## Avoid circular references
from activealarm import ActiveAlarm

