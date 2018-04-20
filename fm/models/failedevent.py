# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# FailedEvent model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import datetime
import time
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import DateTimeField, StringField, EmbeddedDocumentField, ListField
# NOC modules
from noc.sa.models.managedobject import ManagedObject
from noc.lib.nosql import ForeignKeyField, RawDictField
from .eventlog import EventLog


class FailedEvent(Document):
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    """
    Events that caused noc-classifier traceback
    """
    meta = {
        "collection": "noc.events.failed",
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False
    }
    status = "F"
    # Fields
    timestamp = DateTimeField(required=True)
    managed_object = ForeignKeyField(ManagedObject, required=True)
    source = StringField()
    raw_vars = RawDictField(required=True)
    # NOC version caused traceback
    version = StringField(required=True)
    traceback = StringField()
    log = ListField(EmbeddedDocumentField(EventLog))

    def __unicode__(self):
        return u"%s" % self.id
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def mark_as_new(self, message=None):
        """
        Move to unclassified queue
        """
<<<<<<< HEAD
        from noc.core.nsq.pub import nsq_pub
        data = {
            "source": self.source
        }
        data.update(self.raw_vars)
        msg = {
            "id": str(self.id),
            "ts": time.mktime(self.timestamp.timetuple()),
            "object": self.managed_object.id,
            "data": data
        }
        nsq_pub("events.%s" % self.managed_object.pool.name, msg)
        self.delete()
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def log_message(self, message):
        self.log += [EventLog(timestamp=datetime.datetime.now(),
                     from_status=self.status, to_status=self.status,
                     message=message)]
        self.save()
<<<<<<< HEAD
=======

## Avoid circular references
from newevent import NewEvent
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
