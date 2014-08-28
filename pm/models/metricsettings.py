## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MetricSettings model
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db.models import get_model
## Third-party modules
from mongoengine.base import _document_registry
## NOC Modules
from noc.lib.nosql import (Document, EmbeddedDocument, StringField,
                           BooleanField,
                           ListField, EmbeddedDocumentField,
                           PlainReferenceField)
from metricset import MetricSet
from effectivesettings import EffectiveSettings
from noc.lib.solutions import get_solution
from noc.settings import config
from noc.pm.probes.base import probe_registry


class MetricSettingsItem(EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    metric_set = PlainReferenceField(MetricSet)
    is_active = BooleanField(default=True)

    def __unicode__(self):
        return self.metric_set.name


class MetricSettings(Document):
    meta = {
        "collection": "noc.pm.metricsettings",
        "allow_inheritance": False,
        "indexes": [("model_id", "object_id")]
    }

    # Reference to model or document, like sa.ManagedObject
    model_id = StringField()
    # Object id, converted to string
    object_id = StringField()
    # List of metric sets
    metric_sets = ListField(EmbeddedDocumentField(MetricSettingsItem))

    # Object profiles mappings
    # model_id -> profile field name
    OBJECT_PROFILES = {
        "sa.ManagedObject": "object_profile",
        "inv.Interface": "profile"
    }
    _model_cache = {}  # model id -> model class
    _document_cache = {}  # model id -> document

    def __unicode__(self):
        return u"%s:%s" % (self.model_id, self.object_id)

    def _init_document_cache(self):
        for v in _document_registry.itervalues():
            n = "%s.%s" % (v.__module__.split(".")[1],
                           v.__name__)
            self._document_cache[n] = v

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

    def get_object(self):
        return self.get_model().objects.get(id=self.object_id)

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
    def get_settings(cls, object):
        """
        Find MetricSettings instance
        """
        return cls.objects.filter(
            model_id=cls.get_model_id(object),
            object_id=str(object.pk)
        ).first()

    @classmethod
    def get_effective_settings(cls, object, trace=False):
        """
        Returns a list of effective settings for object
        """
        def get_config(name):
            if name in cvars:
                v = cvars[name]
                if isinstance(v, ValueError):
                    raise v
            else:
                try:
                    v = gc(name)
                    cvars[name] = v
                except ValueError, why:
                    cvars[name] = ValueError(why)
                    raise cvars[name]
            return v

        def get_handler(v):
            return "%s.%s.%s" % (
                v.im_class.__module__,
                v.im_class.__name__,
                v.__name__)

        s_seq = []
        # Check profiles
        model_id = cls.get_model_id(object)
        p_field = cls.OBJECT_PROFILES.get(model_id)
        if p_field:
            p = getattr(object, p_field)
            if p:
                ps = cls.get_settings(p)
                if ps:
                    s_seq += [ps]
        # Check object's settings
        s = cls.get_settings(object)
        if s:
            s_seq += [s]
        if not s_seq:
            return []
        mt = {}  # metric type -> metric item
        sr = {}  # metric type -> storage rule
        for s in s_seq:
            for ms in s.metric_sets:
                if not ms.is_active:
                    continue
                for mi in ms.metric_set.get_effective_metrics():
                    mt[mi.metric_type] = mi
                    sr[mi.metric_type] = ms.metric_set.storage_rule
        r = []
        cvars = {}
        gc = getattr(object, "get_probe_config", None)
        # Pass through router solution
        for m, mi in mt.iteritems():
            if not mi.is_active:
                continue
            es = EffectiveSettings(
                object=object,
                model_id=model_id,
                metric=None,
                metric_type=m,
                is_active=True,
                storage_rule=sr[m],
                probe=None,
                interval=sr[m].get_interval(),
                thresholds=[mi.low_error, mi.low_warn,
                            mi.high_warn, mi.high_error]
            )
            _router(object, es)
            if not es.is_active:
                es.error("Deactivated by router")
                r += [es]
                continue
            if not es.metric:
                es.error("No graphite metric found")
                r += [es]
                continue
            if not es.probe:
                es.error("Not assigned to probe daemon")
                r += [es]
                continue
            # Get handler
            for h in probe_registry.iter_handlers(m.name):
                if trace:
                    es.trace("Checking %s" % get_handler(h.handler))
                config = {}
                failed = False
                # Check required parameters
                if h.req:
                    if gc:
                        for name in h.req:
                            try:
                                config[name] = get_config(name)
                            except ValueError:
                                failed = True
                                if trace:
                                    es.trace("Cannot get required variable '%s'" % name)
                                break
                    else:
                        continue
                if failed:
                    if trace:
                        es.trace("Giving up")
                    continue
                # Get optional parameters
                if gc:
                    for name in h.opt:
                        try:
                            config[name] = get_config(name)
                        except ValueError:
                            continue
                # Handler found
                if h.match(config):
                    es.handler = get_handler(h.handler)
                    es.config = config
                    if trace:
                        es.trace("Matched handler %s(%s)" % (
                            get_handler(h.handler), config))
                    break
                elif trace:
                    es.trace("Handler mismatch")
            #
            es.is_active = bool(es.handler)
            if trace and not es.handler:
                if not gc:
                    es.error("No get_probe_config method for %s" % model_id)
                es.error("No handler found")
            if es.is_active or trace:
                r += [es]
        return r


_router = get_solution(config.get("pm", "metric_router")).route
