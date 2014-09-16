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
## Django modules
import django.db.models.signals
## Third-party modules
import mongoengine.signals
## NOC Modules
from noc.lib.nosql import (Document, EmbeddedDocument, StringField,
                           IntField, DictField, DateTimeField,
                           FloatField, ListField, EmbeddedDocumentField)

logger = logging.getLogger(__name__)


class CollectorAddress(EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    proto = StringField()
    address = StringField()
    port = IntField()


class MetricCollectors(EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    policy = StringField(default="prio")
    write_concern = IntField(default=1)
    collectors = ListField(EmbeddedDocumentField(CollectorAddress))


class ProbeConfigMetric(EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }

    metric = StringField()
    metric_type = StringField()
    thresholds = ListField()
    convert = StringField()
    scale = FloatField(default=1.0)
    collectors = EmbeddedDocumentField(MetricCollectors)


class ProbeConfig(Document):
    meta = {
        "collection": "noc.pm.probeconfig",
        "allow_inheritance": False,
        "indexes": [("model_id", "object_id"),
                    ("probe_id", "instance_id"),
                    "uuid", "expire", "changed"]
    }

    # Reference to model or document, like sa.ManagedObject
    model_id = StringField()
    # Object id, converted to string
    object_id = StringField()
    #
    probe_id = StringField()
    instance_id = IntField()
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
    EXPIRE = 3600
    DELETE_DATE = datetime.datetime(2030, 1, 1)

    def __unicode__(self):
        return self.metric

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
    def install(cls):
        mongoengine.signals.class_prepared.connect(cls.on_new_document)
        django.db.models.signals.class_prepared.connect(cls.on_new_model)

    @classmethod
    def on_new_model(cls, sender, *args, **kwargs):
        if hasattr(sender, "get_probe_config"):
            cls.MODELS += [sender]
            django.db.models.signals.post_save.connect(
                cls.on_change_model, sender=sender)
            django.db.models.signals.pre_delete.connect(
                cls.on_delete_model, sender=sender)
            p_field = getattr(sender, "PROFILE_LINK", None)
            if p_field:
                for f in sender._meta.fields:
                    if f.name == p_field:
                        pm = f.rel.to
                        cls.PROFILES[pm] += [(sender, p_field)]
                        break

    @classmethod
    def on_new_document(cls, sender, *args, **kwargs):
        if hasattr(sender, "get_probe_config"):
            cls.MODELS += [sender]
            mongoengine.signals.post_save.connect(
                cls.on_change_document, sender=sender)
            mongoengine.signals.pre_delete.connect(
                cls.on_delete_document, sender=sender)
            p_field = getattr(sender, "PROFILE_LINK", None)
            if p_field:
                pm = sender._fields[p_field].document_type_obj
                cls.PROFILES[pm] += [(sender, p_field)]

    @classmethod
    def _delete_object(cls, object):
        cls._get_collection().update({
                "model_id": cls.get_model_id(object),
                "object_id": str(object.id)
            },
            {
                "$set": {
                    "changed": cls.DELETE_DATE,
                    "expire": cls.DELETE_DATE
                }
            },
            multi=True
        )

    @classmethod
    def _refresh_object(cls, object):
        def get_collector(storage_rule):
            c = collectors.get(storage_rule)
            if c:
                return c
            dc = storage_rule.storage.default_collector
            collectors[storage_rule] = dc
            return dc

        def get_instance(probe, uuid):
            ni = probe.n_instances
            if ni < 1:
                return 0
            else:
                return int(str(uuid)[:8], 16) % ni

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
                collector = get_collector(es.storage_rule)
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
                            "expire": expire,
                            "handler": es.handler,
                            "interval": es.interval,
                            "probe_id": str(es.probe.id),
                            "instance_id": get_instance(es.probe, es.uuid),
                            "config": es.config,
                            "metrics": [{
                                "metric": m.metric,
                                "metric_type": m.metric_type.name,
                                "thresholds": m.thresholds,
                                "convert": m.convert,
                                "scale": m.scale,
                                "collectors": collector
                            } for m in es.metrics]
                        }
                    }
                )
            for m, n in cls.PROFILES[object.__class__]:
                for obj in m.objects.filter(**{n: o.id}):
                    get_refresh_ops(bulk, obj)

        logger.debug("Refresh object %s", object)
        collectors = {}  # Storage rule -> collector url
        # @todo: Make configurable
        now = datetime.datetime.now()
        expire = now + datetime.timedelta(seconds=cls.EXPIRE)
        bulk = cls._get_collection().initialize_ordered_bulk_op()
        get_refresh_ops(bulk, object)
        bulk.execute()

    @classmethod
    def _refresh_config(cls, object):
        def get_collector(storage_rule):
            c = collectors.get(storage_rule)
            if c:
                return c
            dc = storage_rule.storage.default_collector
            collectors[storage_rule] = dc
            return dc

        def get_instance(probe, uuid):
            ni = probe.n_instances
            if ni < 1:
                return 0
            else:
                return int(str(uuid)[:8], 16) % ni

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
                collector = get_collector(es.storage_rule)
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
                            "expire": expire,
                            "handler": es.handler,
                            "interval": es.interval,
                            "probe_id": str(es.probe.id),
                            "instance_id": get_instance(es.probe, es.uuid),
                            "config": es.config,
                            "metrics": [{
                                "metric": m.metric,
                                "metric_type": m.metric_type.name,
                                "thresholds": m.thresholds,
                                "convert": m.convert,
                                "scale": m.scale,
                                "collectors": collector
                            } for m in es.metrics]
                        }
                    }
                )

        logger.debug("Refresh metric config %s", object.name)
        collectors = {}  # Storage rule -> collector url
        # @todo: Make configurable
        now = datetime.datetime.now()
        expire = now + datetime.timedelta(seconds=cls.EXPIRE)
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
    def rebuild(cls, model_id=None):
        pass

## Will be set later
MetricSettings = None
