# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## FailedEvent model
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
from noc.sa.models.managedobject import ManagedObject
from noc.lib import nosql


class FailedEvent(document.Document):
    """
    Events that caused noc-classifier traceback
    """
    meta = {
        "collection": "noc.events.failed",
        "allow_inheritance": False
    }
    status = "F"
    # Fields
    timestamp = fields.DateTimeField(required=True)
    managed_object = nosql.ForeignKeyField(ManagedObject, required=True)
    raw_vars = nosql.RawDictField(required=True)
    # NOC version caused traceback
    version = fields.StringField(required=True)
    traceback = fields.StringField()
    log = fields.ListField(fields.EmbeddedDocumentField(EventLog))

    def __unicode__(self):
        return unicode(self.id)

    def mark_as_new(self, message=None):
        """
        Move to unclassified queue
        """
        if message is None:
            message = "Reclassification requested"
        log = self.log + [EventLog(timestamp=datetime.datetime.now(),
                                   from_status="F", to_status="N",
                                   message=message)]
        e = NewEvent(id=self.id, timestamp=self.timestamp,
                     managed_object=self.managed_object,
                     raw_vars=self.raw_vars,
                     log=log)
        e.save()
        self.delete()
        return e

    def log_message(self, message):
        self.log += [EventLog(timestamp=datetime.datetime.now(),
                     from_status=self.status, to_status=self.status,
                     message=message)]
        self.save()

## Avoid circular references
from newevent import NewEvent
