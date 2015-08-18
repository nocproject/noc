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
import mongoengine.signals
## NOC Modules
from noc.lib.nosql import (Document, EmbeddedDocument, StringField,
                           BooleanField,
                           ListField, EmbeddedDocumentField,
                           PlainReferenceField)
from metricset import MetricSet
from effectivesettings import EffectiveSettings, EffectiveSettingsMetric
from noc.lib.solutions import get_solution
from noc.settings import config
from noc.pm.probes.base import probe_registry
from noc.lib.solutions import get_probe_config


class MetricSettingsItem(EmbeddedDocument):
    metric_set = PlainReferenceField(MetricSet)
    is_active = BooleanField(default=True)

    def __unicode__(self):
        return self.metric_set.name


class MetricSettings(Document):
    meta = {
        "collection": "noc.pm.metricsettings",
        "indexes": [("model_id", "object_id")]
    }

    # Reference to model or document, like sa.ManagedObject
    model_id = StringField()
    # Object id, converted to string
    object_id = StringField()
    # List of metric sets
    metric_sets = ListField(EmbeddedDocumentField(MetricSettingsItem))

    _model_cache = {}  # model id -> model class
    _document_cache = {}  # model id -> document

    def __unicode__(self):
        return u"%s:%s" % (self.model_id, self.object_id)

    def _init_document_cache(self):
        for v in _document_registry.itervalues():
            n = "%s.%s" % (v.__module__.split(".")[1],
                           v.__name__)
            self._document_cache[n] = v
        from noc.pm.models.metricconfig import MetricConfig
        self._document_cache["pm.MetricConfig"] = MetricConfig

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
        m = self.get_model()
        try:
            return m.objects.get(id=self.object_id)
        except m.DoesNotExist:
            return None

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
    def get_effective_settings(cls, object, trace=False, recursive=False):
        """
        Returns a list of effective settings for object
        """
        def get_config(name):
            if name in cvars:
                v = cvars[name]
                if isinstance(v, ValueError):
                    raise v
            else:
                # Try solution first
                try:
                    v = get_probe_config(object, name)
                    cvars[name] = v
                    return v
                except ValueError:
                    pass
                # Use object's get_probe_config
                try:
                    v = gc(name)
                    cvars[name] = v
                except ValueError, why:
                    cvars[name] = ValueError(why)
                    raise cvars[name]
            return v

        def get_recursive():
            r = []
            handler = getattr(object, "iter_recursive_objects", None)
            if recursive and handler:
                for o in handler():
                    r += cls.get_effective_settings(
                        o, trace=trace, recursive=True)
            return r

        s_seq = []
        # Check profiles
        model_id = cls.get_model_id(object)
        p_field = getattr(object, "PROFILE_LINK", None)
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
            return get_recursive()
        mt = {}  # metric type -> metric item
        mti = {}  # metric type -> interval
        for s in s_seq:
            for ms in s.metric_sets:
                if not ms.is_active:
                    continue
                for mi in ms.metric_set.get_effective_metrics():
                    mt[mi.metric_type] = mi
                    mti[mi.metric_type] = ms.metric_set.interval
        r = []
        cvars = {}
        gc = getattr(object, "get_probe_config", None)
        # Pass through router solution
        for m, mi in mt.iteritems():
            if not mi.is_active:
                continue
            try:
                mo = get_config("managed_object")
            except ValueError:
                mo = None
            es = EffectiveSettings(
                object=object,
                model_id=model_id,
                metric=None,
                metric_type=m,
                is_active=True,
                probe=None,
                managed_object=mo,
                interval=mti[m],
                thresholds=[mi.low_error, mi.low_warn,
                            mi.high_warn, mi.high_error]
            )
            _router(object, es)
            if not es.is_active:
                es.error("Deactivated by router")
                if trace:
                    r += [es]
                continue
            if not es.metric:
                es.error("No graphite metric found")
                if trace:
                    r += [es]
                continue
            if not es.probe:
                es.error("Not assigned to probe daemon")
                if trace:
                    r += [es]
                continue
            if not es.probe.storage:
                es.errors("No assigned storage")
                if trace:
                    r += [es]
                continue
            # Get handler
            for h in probe_registry.iter_handlers(m.name):
                if trace:
                    es.trace("Checking %s" % h.handler_name)
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
                    es.handler = h.handler_name
                    es.config = config
                    es.convert = h.convert
                    es.scale = h.scale
                    if trace:
                        es.trace("Matched handler %s(%s)" % (
                            h.handler_name, config))
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
        # Collapse around handlers
        rr = {}
        for es in r:
            probe_id = es.probe.id if es.probe else None
            if es.handler:
                key = (probe_id, es.handler, es.interval)
            else:
                key = (probe_id, es.metric, es.metric_type, es.interval)
            if key in rr:
                e = rr[key]
                e.metrics += [EffectiveSettingsMetric(
                    metric=es.metric, metric_type=es.metric_type,
                    thresholds=es.thresholds, convert=es.convert,
                    scale=es.scale
                )]
            else:
                es.metrics = [EffectiveSettingsMetric(
                    metric=es.metric, metric_type=es.metric_type,
                    thresholds=es.thresholds, convert=es.convert,
                    scale=es.scale
                )]
                es.metric = None
                es.metric_type = None
                es.thresholds = None
                es.convert = None
                es.scale = None
                rr[key] = es
        return rr.values() + get_recursive()


_router = get_solution(config.get("pm", "metric_router")).route

##
from probeconfig import ProbeConfig
mongoengine.signals.post_save.connect(
    ProbeConfig.on_change_metric_settings,
    sender=MetricSettings
)
mongoengine.signals.post_delete.connect(
    ProbeConfig.on_delete_metric_settings,
    sender=MetricSettings
)
