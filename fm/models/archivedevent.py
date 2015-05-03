# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ArchivedEvent model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine import document, fields
## Django modules
from django.template import Template, Context
## NOC modules
from eventlog import EventLog
from eventclass import EventClass
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

    @property
    def subject(self):
        ctx = Context(self.get_template_vars())
        s = Template(self.event_class.subject_template).render(ctx)
        if len(s) >= 255:
            s = s[:125] + " ... " + s[-125:]
        return s

    @property
    def body(self):
        ctx = Context(self.get_template_vars())
        s = Template(self.event_class.body_template).render(ctx)
        return s
