# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ArchivedEvent model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine import document, fields
## NOC modules
from eventlog import EventLog
from eventclass import EventClass
from translation import get_translated_template, get_translated_text
from noc.sa.models.managedobject import ManagedObject
from noc.lib import nosql
from noc.lib.dateutils import total_seconds


class ArchivedEvent(document.Document):
    """
    """
    meta = {
        "collection": "noc.events.archive",
        "allow_inheritance": True,
        "indexes": ["timestamp", "alarms"]
    }
    status = "S"

    timestamp = fields.DateTimeField(required=True)
    managed_object = nosql.ForeignKeyField(ManagedObject, required=True)
    event_class = nosql.PlainReferenceField(EventClass, required=True)
    start_timestamp = fields.DateTimeField(required=True)
    repeats = fields.IntField(required=True)
    raw_vars = nosql.RawDictField()
    resolved_vars = nosql.RawDictField()
    vars = fields.DictField()
    log = fields.ListField(nosql.EmbeddedDocumentField(EventLog))
    alarms = fields.ListField(nosql.ObjectIdField())

    def __unicode__(self):
        return u"%s" % self.id

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
