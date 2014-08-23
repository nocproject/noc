## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MetricSet model
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC Modules
from noc.lib.nosql import (Document, StringField, BooleanField,
                           ListField, EmbeddedDocumentField,
                           PlainReferenceField)
from storagerule import StorageRule
from metrictype import MetricType
from metricitem import MetricItem


class MetricSet(Document):
    meta = {
        "collection": "noc.pm.metricsets",
        "allow_inheritance": False
    }

    name = StringField(unique=True)
    is_active = BooleanField(default=True)
    description = StringField(required=False)
    storage_rule = PlainReferenceField(StorageRule)
    metrics = ListField(EmbeddedDocumentField(MetricItem))

    def __unicode__(self):
        return self.name

    def get_effective_metrics(self):
        """
        Returns a list of MetricItems, containing all effective
        metrics and thresholds for group
        """
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
            nmt = [mt] + sorted(MetricType.objects.filter(name__startswith = mt.name + " | "), key=lambda x: len(x.name))
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
        r = [mi[0] for mi in mt_tree.itervalues() if mi[0].is_active and not mi[1]]
        return r
