## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SyncCache model
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import random
import logging
import uuid
## Django modules
from django.db.models import get_model
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, IntField,
                                DateTimeField, DictField)
from mongoengine.base import _document_registry
## NOC Modules
from noc import settings

logger = logging.getLogger(__name__)


class SyncCache(Document):
    """
    PM Probe daemon
    """
    meta = {
        "collection": "noc.synccaches",
        "allow_inheritance": False,
        "indexes": [("model_id", "object_id"),
                    ("sync_id", "instance_id"),
                    ("sync_id", "instance_id", "expire"),
                    "expire", "changed", "uuid"]
    }

    uuid = StringField()
    # Stringified model id
    model_id = StringField()
    # Stringified object id
    object_id = StringField()
    #
    sync_id = StringField()
    instance_id = IntField()
    # Track expiration and changes
    changed = DateTimeField(default=datetime.datetime.now)
    expire = DateTimeField()
    # Data to sync
    data = DictField()

    DELETE_DATE = datetime.datetime(2030, 1, 1)

    TTL = settings.config.getint("sync", "config_ttl")
    TTL_JITTER = settings.config.getfloat("sync", "config_ttl_jitter")
    TJL = int(TTL - TTL_JITTER * TTL)
    TJH = int(TTL + TTL_JITTER * TTL)

    _model_cache = {}  # model id -> model class
    _document_cache = {}  # model id -> document

    def __unicode__(self):
        return self.uuid

    def _init_document_cache(self):
        for v in _document_registry.itervalues():
            n = "%s.%s" % (v.__module__.split(".")[1],
                           v.__name__)
            self._document_cache[n] = v
        from noc.pm.models.metricconfig import MetricConfig
        self._document_cache["pm.MetricConfig"] = MetricConfig

    @property
    def is_deleted(self):
        return (self.changed == self.expire and
                self.expire == self.DELETE_DATE)

    @property
    def is_expired(self):
        return self.expire <= datetime.datetime.now()

    @classmethod
    def delete_object(cls, object):
        cls._get_collection().update({
                "model_id": cls.get_model_id(object),
                "object_id": str(object.id)
            }, {
                "$set": {
                    "changed": cls.DELETE_DATE,
                    "expire": cls.DELETE_DATE
                }
            },
            multi=True
        )

    @classmethod
    def expire_object(cls, object):
        now = datetime.datetime.now()
        c = cls._get_collection()
        model_id = cls.get_model_id(object)
        c.update({
                "model_id": model_id,
                "object_id": str(object.id)
            }, {
                "$set": {
                    "changed": now,
                    "expire": now
                }
            },
            multi=True
        )

    @classmethod
    def ensure_syncs(cls, object, syncs):
        c = cls._get_collection()
        now = datetime.datetime.now()
        model_id = cls.get_model_id(object)
        object_id = str(object.id)
        r = c.find({
            "model_id": model_id,
            "object_id": object_id
        }, {
            "sync_id": 1
        })
        seen = set(s["sync_id"] for s in r)

        for s in syncs:
            sid = str(s.id)
            if sid in seen:
                seen.remove(sid)
            n = c.find({
                "model_id": model_id,
                "object_id": object_id,
                "sync_id": sid
            }).count()
            if n:
                continue
            logger.debug("Shedule %s %s to sync to %s",
                         model_id, object, s)
            c.insert({
                "uuid": str(uuid.uuid4()),
                "model_id": model_id,
                "object_id": object_id,
                "sync_id": sid,
                "instance_id": 0,
                "changed": now,
                "expire": now
            })
        for s in seen:
            logger.debug("Removing %s %s sync from %s",
                         model_id, object, s)
            c.update({
                "model_id": cls.get_model_id(object),
                "object_id": str(object.id),
                "sync_id": s
            }, {
                "$set": {
                    "changed": cls.DELETE_DATE,
                    "expire": cls.DELETE_DATE
                }
            })

    @classmethod
    def get_ttl(cls):
        if not cls.TTL_JITTER:
            return cls.TTL
        else:
            return random.randint(cls.TJL, cls.TJH)

    @classmethod
    def get_model_id(cls, object):
        if isinstance(object._meta, dict):
            # Document
            return u"%s.%s" % (object.__module__.split(".")[1],
                               object.__class__.__name__)
        else:
            # Model
            return u"%s.%s" % (object._meta.app_label,
                               object._meta.object_name)

    def get_object(self):
        m = self.get_model()
        try:
            return m.objects.get(id=self.object_id)
        except m.DoesNotExist:
            return None

    def get_model(self):
        m = self._model_cache.get(self.model_id)
        if not m:
            # Try django model
            m = get_model(*self.model_id.split("."))
            if not m:
                if not self._document_cache:
                    self._init_document_cache()
                # Try mongoengine model
                m = self._document_cache[self.model_id]
            self._model_cache[self.model_id] = m
        return m

    def refresh(self):
        o = self.get_object()
        logger.debug("Refreshing %s %s (%s)",
                     self.model_id, o, self.uuid)
        if o:
            now = datetime.datetime.now()
            self.data = o.get_sync_data()
            self.changed = now
            self.expire = now + datetime.timedelta(seconds=self.get_ttl())
        else:
            # Deleted object
            logger.debug("Deleting missed object %s", self.uuid)
            self.changed = self.DELETE_DATE
            self.expire = self.DELETE_DATE
        self.save()