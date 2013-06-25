# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ActiveEvent model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## Third-party modules
from mongoengine import document, fields
## NOC modules
from eventlog import EventLog
from eventclass import EventClass
from translation import get_translated_template, get_translated_text
from noc.sa.models.managedobject import ManagedObject
from noc.lib import nosql
from noc.lib.dateutils import total_seconds


class ActiveEvent(document.Document):
    """
    Event in the Active state
    """
    meta = {
        "collection": "noc.events.active",
        "allow_inheritance": False,
        "indexes": ["timestamp", "discriminator", "alarms"]
    }
    status = "A"
    # Fields
    timestamp = fields.DateTimeField(required=True)
    managed_object = nosql.ForeignKeyField(ManagedObject, required=True)
    event_class = nosql.PlainReferenceField(EventClass, required=True)
    start_timestamp = fields.DateTimeField(required=True)
    repeats = fields.IntField(required=True)
    raw_vars = nosql.RawDictField()
    resolved_vars = nosql.RawDictField()
    vars = fields.DictField()
    log = fields.ListField(fields.EmbeddedDocumentField(EventLog))
    discriminator = fields.StringField(required=False)
    alarms = fields.ListField(nosql.ObjectIdField())

    def __unicode__(self):
        return u"%s" % self.id

    def mark_as_new(self, message=None):
        """
        Move to new queue
        """
        if message is None:
            message = "Reclassification requested"
        log = self.log + [EventLog(timestamp=datetime.datetime.now(),
                                   from_status="A", to_status="N",
                                   message=message)]
        e = NewEvent(id=self.id, timestamp=self.timestamp,
                     managed_object=self.managed_object,
                     raw_vars=self.raw_vars,
                     log=log)
        e.save()
        self.delete()
        return e

    def mark_as_failed(self, version, traceback):
        """
        Move event into noc.events.failed
        """
        message = "Failed to classify on NOC version %s" % version
        log = self.log + [EventLog(timestamp=datetime.datetime.now(),
                                   from_status="N", to_status="F",
                                   message=message)]
        e = FailedEvent(id=self.id, timestamp=self.timestamp,
                        managed_object=self.managed_object,
                        raw_vars=self.raw_vars, version=version,
                        traceback=traceback, log=log)
        e.save()
        self.delete()
        return e

    def mark_as_archived(self, message):
        log = self.log + [EventLog(timestamp=datetime.datetime.now(),
                                   from_status="A", to_status="S",
                                   message=message)]
        e = ArchivedEvent(
            id=self.id,
            timestamp=self.timestamp,
            managed_object=self.managed_object,
            event_class=self.event_class,
            start_timestamp=self.start_timestamp,
            repeats=self.repeats,
            raw_vars=self.raw_vars,
            resolved_vars=self.resolved_vars,
            vars=self.vars,
            log=log,
            alarms=self.alarms
        )
        e.save()
        self.delete()
        return e

    def drop(self):
        """
        Mark event to be dropped. Only for use from event trigger pyrule.
        All further operations on event may lead to unpredictable results.
        Event actually deleted by noc-classifier
        """
        self.id = None

    @property
    def to_drop(self):
        """
        Check event marked to be dropped
        """
        return self.id is None

    def log_message(self, message):
        self.log += [EventLog(timestamp=datetime.datetime.now(),
                     from_status=self.status, to_status=self.status,
                     message=message)]
        self.save()

    def log_suppression(self, timestamp):
        """
        Increate repeat count and update timestamp, if required
        """
        self.repeats += 1
        if timestamp > self.timestamp:
            self.timestamp = timestamp
        self.save()

    @property
    def duration(self):
        """
        Logged event duration in seconds
        """
        return total_seconds(self.timestamp - self.start_timestamp)

    def get_template_vars(self):
        """
        Prepare template variables
        """
        vars = self.vars.copy()
        vars.update({"event": self})
        return vars

    def get_translated_subject(self, lang):
        s = get_translated_template(lang, self.event_class.text,
                                    "subject_template",
                                    self.get_template_vars())
        if len(s) >= 255:
            s = s[:125] + " ... " + s[-125:]
        return s

    def get_translated_body(self, lang):
        return get_translated_template(lang, self.event_class.text,
                                       "body_template",
                                       self.get_template_vars())

    def get_translated_symptoms(self, lang):
        return get_translated_text(
            lang, self.event_class.text, "symptoms")

    def get_translated_probable_causes(self, lang):
        return get_translated_text(
            lang, self.event_class.text, "probable_causes")

    def get_translated_recommended_actions(self, lang):
        return get_translated_text(
            lang, self.event_class.text, "recommended_actions")

    @property
    def managed_object_id(self):
        """
        Hack to return managed_object.id without SQL lookup
        """
        o = self._data["managed_object"]
        if type(o) in (int, long):
            return o
        return o.id

## Avoid circular references
from newevent import NewEvent
from failedevent import FailedEvent
from archivedevent import ArchivedEvent
