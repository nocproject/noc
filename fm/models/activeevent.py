# ---------------------------------------------------------------------
# ActiveEvent model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
from threading import Lock
from typing import Any, Optional, Union
import time

# Third-party modules
from jinja2 import Template as Jinja2Template
from mongoengine.document import Document
from mongoengine.fields import (
    StringField,
    DateTimeField,
    IntField,
    ListField,
    EmbeddedDocumentField,
    DictField,
    ObjectIdField,
    BinaryField,
)
from bson import ObjectId

# NOC modules
from noc.sa.models.managedobject import ManagedObject
from noc.core.cache.decorator import cachedmethod
from noc.core.mongo.fields import ForeignKeyField, PlainReferenceField, RawDictField
from .eventlog import EventLog
from .eventclass import EventClass

id_lock = Lock()


class ActiveEvent(Document):
    """
    Event in the Active state
    """

    meta = {
        "collection": "noc.events.active",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            "timestamp",
            "#reference",
            "alarms",
            ("timestamp", "event_class", "managed_object"),
            {"fields": ["expires"], "expireAfterSeconds": 0},
        ],
    }
    status = "A"
    # Fields
    timestamp = DateTimeField(required=True)
    managed_object = ForeignKeyField(ManagedObject, required=True)
    event_class = PlainReferenceField(EventClass, required=True)
    start_timestamp = DateTimeField(required=True)
    repeats = IntField(required=True)
    source = StringField()
    raw_vars = RawDictField()
    resolved_vars = RawDictField()
    vars = DictField()
    log = ListField(EmbeddedDocumentField(EventLog))
    reference = BinaryField(required=False)
    alarms = ListField(ObjectIdField())
    expires = DateTimeField(required=False)

    def __str__(self):
        return "%s" % self.id

    @classmethod
    @cachedmethod(key="activeevent-%s", lock=lambda _: id_lock, ttl=900)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["ActiveEvent"]:
        return ActiveEvent.objects.filter(id=oid).first()

    def mark_as_new(self, message=None):
        """
        Move to new queue for reclassification
        @todo: Rename method to *reclassify*
        """
        import orjson
        from noc.core.service.loader import get_service

        # if message is None:
        #    message = "Reclassification requested"
        # log = self.log + [EventLog(timestamp=datetime.datetime.now(),
        #                            from_status="A", to_status="N",
        #                            message=message)]
        data = {"source": self.source}
        data.update(self.raw_vars)
        msg = {
            "id": str(self.id),
            "ts": time.mktime(self.timestamp.timetuple()),
            "object": self.managed_object.id,
            "data": data,
        }
        stream, partition = self.managed_object.events_stream_and_partition
        svc = get_service()
        svc.publish(
            orjson.dumps(msg),
            stream=stream,
            partition=partition,
        )
        self.delete()

    def mark_as_failed(self, version, traceback):
        """
        Move event into noc.events.failed
        """
        message = "Failed to classify on NOC version %s" % version
        log = self.log + [
            EventLog(
                timestamp=datetime.datetime.now(), from_status="N", to_status="F", message=message
            )
        ]
        e = FailedEvent(
            id=self.id,
            timestamp=self.timestamp,
            managed_object=self.managed_object,
            source=self.source,
            raw_vars=self.raw_vars,
            version=version,
            traceback=traceback,
            log=log,
        )
        e.save()
        self.delete()
        return e

    def mark_as_archived(self, message):
        log = self.log + [
            EventLog(
                timestamp=datetime.datetime.now(), from_status="A", to_status="S", message=message
            )
        ]
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
            alarms=self.alarms,
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
        self.log += [
            EventLog(
                timestamp=datetime.datetime.now(),
                from_status=self.status,
                to_status=self.status,
                message=message,
            )
        ]
        self.save()

    @classmethod
    def log_suppression(cls, event_id: ObjectId, timestamp: datetime.datetime):
        """
        Increase repeat count and update timestamp, if required
        """
        ActiveEvent._get_collection().update_one(
            {"_id": event_id}, {"$inc": {"repeats": 1}, "$set": {"timestamp": timestamp}}
        )

    @property
    def duration(self):
        """
        Logged event duration in seconds
        """
        return (self.timestamp - self.start_timestamp).total_seconds()

    def get_template_vars(self):
        """
        Prepare template variables
        """
        vars = self.vars.copy()
        vars.update({"event": self})
        return vars

    @property
    def subject(self):
        s = Jinja2Template(self.event_class.subject_template).render(self.get_template_vars())
        if len(s) >= 255:
            s = s[:125] + " ... " + s[-125:]
        return s

    @property
    def body(self):
        s = Jinja2Template(self.event_class.body_template).render(self.get_template_vars())
        return s

    @property
    def managed_object_id(self):
        """
        Hack to return managed_object.id without SQL lookup
        """
        o = self._data["managed_object"]
        if hasattr(o, "id"):
            return o.id
        return o

    def contribute_to_alarm(self, alarm):
        if alarm.id in self.alarms:
            return
        self._get_collection().update_one(
            {"_id": self.id}, {"$set": {"expires": None}, "$push": {"alarms": alarm.id}}
        )
        self.alarms.append(alarm.id)
        self.expires = None

    def do_not_dispose(self):
        """
        Skip dispose
        :return:
        """
        self._do_not_dispose = True

    @property
    def to_dispose(self):
        if not self.event_class:
            return True
        if hasattr(self, "_do_not_dispose"):
            return False
        return len(self.event_class.disposition) > 0

    def set_hint(self, k: str, v: Any) -> None:
        if not hasattr(self, "_hints"):
            setattr(self, "_hints", {})
        self._hints[k] = v

    def get_hint(self, k: str) -> Optional[Any]:
        h = getattr(self, "_hints", None)
        if not h:
            return None
        return h.get(k)

    @classmethod
    def create_from_dict(cls, d: dict):
        """
        Create instance from dict with data from clickhouse
        """
        return cls(
            id=d["id"],
            timestamp=datetime.datetime.strptime(d["timestamp"], "%Y-%m-%d %H:%M:%S"),
            managed_object=ManagedObject.get_by_bi_id(d["managed_object_bi_id"]),
            event_class=EventClass.get_by_bi_id(d["event_class_bi_id"]),
            start_timestamp=datetime.datetime.strptime(d["start_timestamp"], "%Y-%m-%d %H:%M:%S"),
            source=d["source"],
            raw_vars=d["raw_vars"],
            resolved_vars=d["resolved_vars"],
            vars=d["vars"],
            alarms=d["alarms"],
        )


# Avoid circular references
from .failedevent import FailedEvent
from .archivedevent import ArchivedEvent
