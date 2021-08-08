# ---------------------------------------------------------------------
# FailedEvent model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import time

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import DateTimeField, StringField, EmbeddedDocumentField, ListField
import orjson

# NOC modules
from noc.sa.models.managedobject import ManagedObject
from noc.core.mongo.fields import ForeignKeyField, RawDictField
from .eventlog import EventLog


class FailedEvent(Document):
    """
    Events that caused noc-classifier traceback
    """

    meta = {"collection": "noc.events.failed", "strict": False, "auto_create_index": False}
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

    def __str__(self):
        return "%s" % self.id

    def mark_as_new(self, message=None):
        """
        Move to unclassified queue
        """
        from noc.core.service.pub import publish

        data = {"source": self.source}
        data.update(self.raw_vars)
        msg = {
            "id": str(self.id),
            "ts": time.mktime(self.timestamp.timetuple()),
            "object": self.managed_object.id,
            "data": data,
        }
        stream, partition = self.managed_object.events_stream_and_partition
        publish(
            orjson.dumps(msg),
            stream=stream,
            partition=partition,
        )

        self.delete()

    def log_message(self, message):
        self.log += [
            EventLog(
                timestamp=datetime.datetime.now(),
                from_status=self.status,
                to_status=self.status,
                message=message,
            )
        ]
        self.save()
