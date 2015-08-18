## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Full-text search queue
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## Django modules
from django.db.models import signals as django_signals
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField

logger = logging.getLogger(__name__)


class FTSQueue(Document):
    meta = {
        "collection": "noc.fts_queue",
        "allow_inheritance": False
    }

    object = StringField(unique=True)  # <module>.<Model>:<id>
    op = StringField(choices=[("U", "Update"), ("D", "Delete")])

    models = {}  # FTS models

    def unicode(self):
        return "%s:%s" % (self.object, self.op)

    @classmethod
    def schedule_update(cls, o):
        oid = cls.get_id(o)
        logger.debug("Scheduling FTS update for %s (%s)", oid, o)
        cls._get_collection().update(
            {
                "object": oid
            }, {
                "$set": {
                    "object": oid,
                    "op": "U"
                }
            },
            upsert=True
        )
        cls.schedule_job()

    @classmethod
    def schedule_delete(cls, o):
        oid = cls.get_id(o)
        logger.debug("Scheduling FTS delete for %s (%s)", oid, o)
        cls._get_collection().update(
            {
                "object": oid
            }, {
                "$set": {
                    "object": oid,
                    "op": "D"
                }
            },
            upsert=True
        )
        cls.schedule_job()

    @classmethod
    def schedule_job(cls):
        # sliding_job("main.jobs", "main.update_index",
        #            delta=5, cutoff_delta=15)
        pass

    @classmethod
    def on_update_model(cls, sender, instance, **kwargs):
        cls.schedule_update(instance)

    @classmethod
    def on_delete_model(cls, sender, instance, **kwargs):
        cls.schedule_delete(instance)

    @classmethod
    def get_id(cls, o):
        return "%s:%s" % (o._meta, o.id)

    @classmethod
    def get_object(cls, id):
        """
        Get object by FTS id
        """
        m, i = id.split(":")
        if not m in cls.models:
            return None
        model = cls.models[m]
        try:
            return model.objects.get(id=int(i))
        except model.DoesNotExist:
            return None


def full_text_search(cls):
    """
    Decorator to denote models supporting full text search

    @full_text_search
    class MyModel(Model):
        ...
        def get_index(self):
            return {
                "id": ...,
                "title": ....,
                "content": ....,
                "card": ....,
                "tags": ...
            }
    """
    assert hasattr(cls, "get_index")
    logger.debug("Adding FTS index for %s", cls._meta)
    FTSQueue.models[str(cls._meta)] = cls
    django_signals.post_save.connect(FTSQueue.on_update_model,
                                     sender=cls)
    django_signals.post_delete.connect(FTSQueue.on_delete_model,
                                       sender=cls)
    return cls
