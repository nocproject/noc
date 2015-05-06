# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NewEvent model
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


class NewEvent(document.Document):
    """
    Raw unclassified event as written by SAE or collector
    """
    meta = {
        "collection": "noc.events.new",
        "allow_inheritance": False,
        "indexes": ["seq"]
    }
    status = "N"
    # Fields
    timestamp = fields.DateTimeField(required=True)
    managed_object = nosql.ForeignKeyField(ManagedObject, required=True)
    raw_vars = nosql.RawDictField(required=True)
    log = fields.ListField(fields.EmbeddedDocumentField(EventLog))
    seq = fields.BinaryField(max_bytes=8, required=False)

    def __unicode__(self):
        return unicode(self.id)

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

    @property
    def source(self):
        """
        Event source or None
        """
        if self.raw_vars and "source" in self.raw_vars:
            return self.raw_vars["source"]
        return None

    def log_message(self, message):
        self.log += [EventLog(timestamp=datetime.datetime.now(),
                     from_status=self.status, to_status=self.status,
                     message=message)]
        self.save()

## Avoid circular references
from failedevent import FailedEvent
