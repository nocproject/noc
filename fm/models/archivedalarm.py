# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ArchivedAlarm model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## NOC modules
import noc.lib.nosql as nosql
from noc.sa.models.managedobject import ManagedObject
from alarmclass import AlarmClass
from alarmlog import AlarmLog
from alarmseverity import AlarmSeverity
from translation import get_translated_template, get_translated_text


class ArchivedAlarm(nosql.Document):
    meta = {
        "collection": "noc.alarms.archived",
        "allow_inheritance": False,
        "indexes": ["root"]
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
        vars.update({"event": self})
        return vars

    def get_translated_subject(self, lang):
        s = get_translated_template(lang, self.alarm_class.text,
                                    "subject_template",
                                    self.get_template_vars())
        if len(s) >= 255:
            s = s[:125] + " ... " + s[-125:]
        return s

    def get_translated_body(self, lang):
        return get_translated_template(lang, self.alarm_class.text,
                                       "body_template",
                                       self.get_template_vars())

    def get_translated_symptoms(self, lang):
        return get_translated_text(
            lang, self.alarm_class.text, "symptoms")

    def get_translated_probable_causes(self, lang):
        return get_translated_text(
            lang, self.alarm_class.text, "probable_causes")

    def get_translated_recommended_actions(self, lang):
        return get_translated_text(
            lang, self.alarm_class.text, "recommended_actions")

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
