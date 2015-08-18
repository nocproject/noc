## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ProbeConfig model
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from collections import defaultdict
import datetime
import logging
import random
## Django modules
import django.db.models.signals
## Third-party modules
import mongoengine.signals
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField, IntField, DictField, DateTimeField, FloatField,
    ListField, EmbeddedDocumentField)
## NOC Modules
from noc import settings

logger = logging.getLogger(__name__)


class ProbeConfigMetric(EmbeddedDocument):
    metric = StringField()
    metric_type = StringField()
    thresholds = ListField()
    convert = StringField()
    scale = FloatField(default=1.0)


class ProbeConfig(Document):
    meta = {
        "collection": "noc.pm.probeconfig",
        "indexes": [("model_id", "object_id"),
                    "pool",
                    ("pool", "expire"),
                    "uuid", "expire", "changed", "metrics.metric"]
    }

    # Reference to model or document, like sa.ManagedObject
    model_id = StringField()
    # Object id, converted to string
    object_id = StringField()
    #
    pool = StringField()
    #
    managed_object = IntField(required=False)
    #
    uuid = StringField()
    #
    changed = DateTimeField(default=datetime.datetime.now)
    expire = DateTimeField()
    # Configuration section
    handler = StringField()
    interval = IntField()
    config = DictField()
    metrics = ListField(EmbeddedDocumentField(ProbeConfigMetric))

    PROFILES = defaultdict(list)  # model -> [(model, field), ...]
    MODELS = []
    TTL = settings.config.getint("pm", "config_ttl")
    TTL_JITTER = settings.config.getfloat("pm", "config_ttl_jitter")
    TJL = int(TTL - TTL_JITTER * TTL)
    TJH = int(TTL + TTL_JITTER * TTL)

    DELETE_DATE = datetime.datetime(2030, 1, 1)

    def __unicode__(self):
        return unicode(self.uuid)

    @property
    def is_deleted(self):
        return (self.changed == self.expire and
                self.expire == self.DELETE_DATE)

    @property
    def is_expired(self):
        return self.expire <= datetime.datetime.now()

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
        return MetricSettings(
            model_id=self.model_id,
            object_id=self.object_id
        ).get_object()

    @classmethod
    def _delete_object(cls, object):
        model_id = cls.get_model_id(object)
        object_id = str(object.id)
        # Mark probeconfig as deleted
        logger.debug("Marking ProbeConfig as deleted: %s:%s",
                     model_id, object_id)
        cls._get_collection().update({
                "model_id": model_id,
                "object_id": object_id
            },
            {
                "$set": {
                    "changed": cls.DELETE_DATE,
                    "expire": cls.DELETE_DATE
                }
            },
            multi=True
        )
        # wipe out metricsettings
        logger.debug("Deleting MetricSettings: %s:%s",
                     model_id, object_id)
        MetricSettings._get_collection().remove({
            "model_id": model_id,
            "object_id": object_id
        })

    @classmethod
    def get_ttl(cls):
        if not cls.TTL_JITTER:
            return cls.TTL
        else:
            return random.randint(cls.TJL, cls.TJH)

    @classmethod
    def _refresh_object(cls, object):
        def get_refresh_ops(bulk, o):
            model_id = cls.get_model_id(o)
            logger.debug("Bulk refresh %s %s", model_id, o)
            # Cleanup
            bulk.find(
                {
                    "model_id": model_id,
                    "object_id": str(o.id)
                }
            ).update(
                {
                    "$set": {
                        "changed": cls.DELETE_DATE,
                        "expire": cls.DELETE_DATE
                    }
                }
            )
            for es in MetricSettings.get_effective_settings(o):
                if es.managed_object:
                    mo = es.managed_object.id
                else:
                    mo = None
                bulk.find(
                    {
                        "uuid": es.uuid
                    }
                ).upsert().update(
                    {
                        "$set": {
                            "model_id": es.model_id,
                            "object_id": str(es.object.id) if es.object else None,
                            "changed": now,
                            "expire": now + datetime.timedelta(seconds=cls.get_ttl()),
                            "handler": es.handler,
                            "interval": es.interval,
                            "pool": str(es.pool),
                            "config": es.config,
                            "managed_object": mo,
                            "metrics": [{
                                "metric": m.metric,
                                "metric_type": m.metric_type.name,
                                "thresholds": m.thresholds,
                                "convert": m.convert,
                                "scale": m.scale
                            } for m in es.metrics]
                        }
                    }
                )
            for m, n in cls.PROFILES[o.__class__]:
                for obj in m.objects.filter(**{n: o.id}):
                    get_refresh_ops(bulk, obj)

        logger.debug("Refresh object %s", object)
        # @todo: Make configurable
        now = datetime.datetime.now()
        bulk = cls._get_collection().initialize_ordered_bulk_op()
        get_refresh_ops(bulk, object)
        bulk.execute()

    @classmethod
    def _refresh_config(cls, object):
        def get_refresh_ops(bulk, o):
            model_id = cls.get_model_id(o)
            logger.debug("Bulk refresh %s %s", model_id, o)
            # Cleanup
            bulk.find(
                {
                    "model_id": "pm.MetricConfig",
                    "object_id": str(o.id)
                }
            ).update(
                {
                    "$set": {
                        "changed": cls.DELETE_DATE,
                        "expire": cls.DELETE_DATE
                    }
                }
            )
            for es in o.get_effective_settings():
                bulk.find(
                    {
                        "uuid": es.uuid
                    }
                ).upsert().update(
                    {
                        "$set": {
                            "model_id": "pm.MetricConfig",
                            "object_id": str(o.id),
                            "changed": now,
                            "expire": now + datetime.timedelta(seconds=cls.get_ttl()),
                            "handler": es.handler,
                            "interval": es.interval,
                            "pool": str(es.pool),
                            "config": es.config,
                            "metrics": [{
                                "metric": m.metric,
                                "metric_type": m.metric_type.name,
                                "thresholds": m.thresholds,
                                "convert": m.convert,
                                "scale": m.scale
                            } for m in es.metrics]
                        }
                    }
                )

        logger.debug("Refresh metric config %s", object.name)
        # @todo: Make configurable
        now = datetime.datetime.now()
        bulk = cls._get_collection().initialize_ordered_bulk_op()
        get_refresh_ops(bulk, object)
        bulk.execute()

    @classmethod
    def on_change_model(cls, sender, instance, *args, **kwargs):
        cls._refresh_object(instance)

    @classmethod
    def on_change_document(cls, sender, document=None, *args, **kwargs):
        cls._refresh_object(document)

    @classmethod
    def on_delete_model(cls, sender, instance, *args, **kwargs):
        cls._delete_object(instance)
        # Rebuild configs for related objects
        for m, n in cls.PROFILES[sender]:
            for obj in m.objects.filter(**{n: instance.id}):
                cls._refresh_object(obj)

    @classmethod
    def on_delete_document(cls, sender, document, *args, **kwargs):
        cls._delete_object(document)
        # Rebuild configs for related objects
        for m, n in cls.PROFILES[sender]:
            for obj in m.objects.filter(**{n: document.id}):
                cls._refresh_object(obj)

    @classmethod
    def on_change_metric_settings(cls, sender, document=None, *args, **kwargs):
        object = document.get_object()
        logger.debug("Apply changed MetricSettings for '%s'", object)
        cls._refresh_object(object)
        if not document.metric_sets:
            logger.debug("Delete empty MetricSettings for %s", object)
            document.delete()

    @classmethod
    def on_delete_metric_settings(cls, sender, document, *args, **kwargs):
        object = document.get_object()
        logger.debug("Apply deleted MetricSettings for '%s'", object)
        cls._refresh_object(object)

    @classmethod
    def on_change_metric_config(cls, sender, document=None, *args, **kwargs):
        logger.debug("Apply changed MetricConfig for '%s'", document.name)
        cls._refresh_config(document)

    @classmethod
    def on_delete_metric_config(cls, sender, document, *args, **kwargs):
        logger.debug("Apply deleted MetricConfig for '%s'", document.name)
        cls._delete_object(document)

    @classmethod
    def on_change_metric_set(cls, sender, document=None, *args, **kwargs):
        logger.info("Applying changes to MetricSet '%s'", document.name)
        # Find all affected metric settings
        for ms in MetricSettings.objects.filter(
                metric_sets__metric_set=document.id):
            cls._refresh_object(ms.get_object())

    @classmethod
    def on_delete_metric_set(cls, sender, document, *args, **kwargs):
        logger.info("Deleting MetricSet '%s'", document.name)
        for ms in MetricSettings.objects.filter(
            metric_sets__metric_set=document.id
        ):
            ms.metric_sets = [s for s in ms.metric_sets
                              if s.metric_set.id != document.id]
            ms.save()  # Triggers refresh_object

    @classmethod
    def on_change_auth_profile(cls, sender, instance, *args, **kwargs):
        logger.info("Applying changes to AuthProfile '%s'" % instance.name)
        for mo in instance.managedobject_set.all():
            cls._refresh_object(mo)

    @classmethod
    def on_change_object_caps(cls, sender, document=None, *args, **kwargs):
        logger.info("Applying changes to object capabilities '%s'", document.object.name)
        cls.on_change_model(document.object, document.object)

    def refresh(self):
        logger.debug("Refreshing %s", self.uuid)
        o = self.get_object()
        if not o:
            return
        if self.model_id == "pm.MetricConfig":
            self._refresh_config(o)
        else:
            self._refresh_object(o)

    @classmethod
    def rebuild(cls, model_id=None):
        pass


def probe_config(cls):
    """
    Decorator to denote models/documents for probe configuration

    @probe_config
    class MyDocument(Document):
        ...
        def get_probe_config(self, config):
            ...
    """
    if cls in ProbeConfig.MODELS:
        return cls
    assert hasattr(cls, "get_probe_config")
    logger.debug("Registering model %s" % cls.__name__)
    ProbeConfig.MODELS += [cls]
    if isinstance(cls._meta, dict):
        # Document
        mongoengine.signals.post_save.connect(
            ProbeConfig.on_change_document, sender=cls)
        mongoengine.signals.pre_delete.connect(
            ProbeConfig.on_delete_document, sender=cls)
        p_field = getattr(cls, "PROFILE_LINK", None)
        if p_field:
            pm = cls._fields[p_field].document_type_obj
            ProbeConfig.PROFILES[pm] += [(cls, p_field)]
    else:
        # Model
        django.db.models.signals.post_save.connect(
            ProbeConfig.on_change_model, sender=cls)
        django.db.models.signals.pre_delete.connect(
            ProbeConfig.on_delete_model, sender=cls)
        p_field = getattr(cls, "PROFILE_LINK", None)
        if p_field:
            for f in cls._meta.fields:
                if f.name == p_field:
                    pm = f.rel.to
                    ProbeConfig.PROFILES[pm] += [(cls, p_field)]
                    break

    return cls

##
from metricsettings import MetricSettings
