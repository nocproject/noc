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
## Django modules
import django.db.models.signals
## Third-party modules
import mongoengine.signals
## NOC Modules
from noc.lib.nosql import (Document, StringField,
                           IntField, DictField, DateTimeField,
                           ListField, ObjectIdField)


class ProbeConfig(Document):
    meta = {
        "collection": "noc.pm.probeconfig",
        "allow_inheritance": False,
        "indexes": [("model_id", "object_id"), "probe_id", "uuid",
                    "expire", "changed"]
    }

    # Reference to model or document, like sa.ManagedObject
    model_id = StringField()
    # Object id, converted to string
    object_id = StringField()
    #
    probe_id = StringField()
    #
    uuid = StringField()
    #
    changed = DateTimeField(default=datetime.datetime.now)
    expire = DateTimeField()
    # Configuration section
    metric = StringField(unique=True)
    metric_type = StringField()
    handler = StringField()
    interval = IntField()
    thresholds = ListField()
    config = DictField()

    PROFILES = defaultdict(list)  # model -> [(model, field), ...]
    MODELS = []

    def __unicode__(self):
        return self.metric

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

    @classmethod
    def install(cls):
        mongoengine.signals.class_prepared.connect(cls.on_new_document)
        django.db.models.signals.class_prepared.connect(cls.on_new_model)

    @classmethod
    def on_new_model(cls, sender, *args, **kwargs):
        if hasattr(sender, "get_probe_config"):
            cls.MODELS += [sender]
            django.db.models.signals.post_save.connect(cls.on_change_model)
            django.db.models.signals.pre_delete.connect(cls.on_delete)
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
            mongoengine.signals.post_save.connect(cls.on_change_document)
            mongoengine.signals.pre_delete.connect(cls.on_delete)
            p_field = getattr(sender, "PROFILE_LINK", None)
            if p_field:
                pm = sender._fields[p_field].document_type_obj
                cls.PROFILES[pm] += [(sender, p_field)]

    @classmethod
    def clean_for_object(cls, object):
        cls._get_collection().remove(
            {
                "model_id": cls.get_model_id(object),
                "object_id": str(object.id)
            },
            multi=True
        )

    @classmethod
    def refresh_object(cls, object):
        # @todo: Make configurable
        now = datetime.datetime.now()
        expire = now + datetime.timedelta(seconds=3600)
        config = [{
            "uuid": es.uuid,
            "model_id": es.model_id,
            "object_id": str(es.object.id) if es.object else None,
            "changed": now,
            "expire": expire,
            "metric": es.metric,
            "metric_type": es.metric_type.name,
            "handler": es.handler,
            "interval": es.interval,
            "thresholds": es.thresholds,
            "probe_id": str(es.probe.id),
            "config": es.config
        } for es in MetricSettings.get_effective_settings(object)]
        cls.clean_for_object(object)
        if config:
            cls._get_collection().insert(config)
        for m, n in cls.PROFILES[object.__class__]:
            for obj in m.objects.filter(**{n: object.id}):
                cls.refresh_object(obj)

    @classmethod
    def on_change_model(cls, sender, instance, *args, **kwargs):
        cls.refresh_object(instance)

    @classmethod
    def on_change_document(cls, sender, document=None, *args, **kwargs):
        cls.refresh_object(document)

    @classmethod
    def on_delete(cls, sender, instance, *args, **kwargs):
        cls.clean_for_object(instance)
        # Rebuild configs for related objects
        for m, n in cls.PROFILES[sender]:
            for obj in m.objects.filter(**{n: instance.id}):
                cls.refresh_object(obj)

    @classmethod
    def rebuild(cls, model_id=None):
        pass

## Will be set later
MetricSettings = None
