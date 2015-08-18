## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MetricConfig model
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## Third-party modules
import mongoengine.signals
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, BooleanField, ListField,
                                EmbeddedDocumentField, ReferenceField,
                                DictField, IntField)
from mongoengine.queryset.base import DENY
## NOC Modules
from metrictype import MetricType
from metricitem import MetricItem
from noc.main.models.pool import Pool
from effectivesettings import EffectiveSettings, EffectiveSettingsMetric
from noc.pm.probes.base import probe_registry

logger = logging.getLogger(__name__)


class MetricConfig(Document):
    meta = {
        "collection": "noc.pm.metricconfigs"
    }

    name = StringField(unique=True)
    is_active = BooleanField(default=True)
    handler = StringField()
    interval = IntField(default=60)
    description = StringField(required=False)
    pool = ReferenceField(Pool, reverse_delete_rule=DENY, required=True)
    metrics = ListField(EmbeddedDocumentField(MetricItem))
    config = DictField(default={})

    def __unicode__(self):
        return self.name

    def get_effective_settings(self, trace=False):
        """
        Returns a list of MetricItems, containing all effective
        metrics and thresholds for group
        """
        def q(s):
            return s.replace(" | ", ".").replace(" ", "_").replace("/", "-").lower()

        def apply_settings(name, mi):
            """
            Apply settings to node and all children
            """
            dst = mt_tree[name][0]
            dst.is_active = mi.is_active
            dst.low_warn = mi.low_warn
            dst.high_warn = mi.high_warn
            dst.low_error = mi.low_error
            dst.high_error = mi.high_error
            for c in mt_tree[name][1]:
                apply_settings(c, mi)

        # Build metric type tree
        mt_tree = {}  # Metric type name -> (metric item, [children])
        for mi in self.metrics:
            mt = mi.metric_type
            if mt.name in mt_tree:
                continue
            # Find all children
            nmt = [mt] + sorted(
                MetricType.objects.filter(
                    name__startswith=mt.name + " | "),
                key=lambda x: len(x.name))
            for m in nmt:
                if m.name in mt_tree:
                    continue
                mt_tree[m.name] = [
                    MetricItem(metric_type=m, is_active=True),
                    []
                ]
                parent = " | ".join(p for p in m.name.split(" | ")[:-1])
                if parent in mt_tree:
                    mt_tree[parent][1] += [m.name]
        # Apply settings
        for mi in self.metrics:
            apply_settings(mi.metric_type.name, mi)
        # Fetch leaf nodes
        r = []
        mt = [mi[0] for mi in mt_tree.itervalues() if not mi[1]]
        for mi in mt:
            if not mi.is_active:
                continue
            if mi.metric:
                metric = mi.metric
            else:
                # Auto-generate metric
                metric = "metric.%s.%s" % (q(self.name), q(mi.metric_type.name))
            es = EffectiveSettings(
                object=self,
                model_id="pm.MetricConfig",
                metric=metric,
                metric_type=mi.metric_type,
                is_active=True,
                pool=self.pool.name,
                interval=self.interval,
                thresholds=[mi.low_error, mi.low_warn,
                            mi.high_warn, mi.high_error]
            )
            for h in probe_registry.iter_class_handlers(
                    self.handler, mi.metric_type.name):
                if trace:
                    es.trace("Checking %s" % h.handler_name)
                config = {}
                failed = False
                if h.req:
                    for name in h.req:
                        if name in self.config and self.config[name] not in ("", None):
                            config[name] = self.config[name]
                        else:
                            failed = True
                            if trace:
                                es.trace("Cannot get required variable '%s'" % name)
                            break
                if failed:
                    if trace:
                        es.trace("Giving up")
                    continue
                # Get optional parameters
                for name in h.opt:
                    if name in self.config and self.config[name] not in ("", None):
                        config[name] = self.config[name]
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
                es.error("No handler found")
            if es.is_active or trace:
                r += [es]
        # Collapse around handlers
        rr = {}
        for es in r:
            pool = es.pool if es.pool else None
            if es.handler:
                key = (pool, es.handler, es.interval)
            else:
                key = (pool, es.metric, es.metric_type, es.interval)
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
        return rr.values()

##
from probeconfig import ProbeConfig
mongoengine.signals.post_save.connect(
    ProbeConfig.on_change_metric_config,
    sender=MetricConfig
)
mongoengine.signals.post_delete.connect(
    ProbeConfig.on_delete_metric_config,
    sender=MetricConfig
)

