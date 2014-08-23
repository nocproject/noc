## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MetricItem model
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC Modules
from noc.lib.nosql import EmbeddedDocument, BooleanField, FloatField, PlainReferenceField
from metrictype import MetricType


class MetricItem(EmbeddedDocument):
    meta = {
        "allow_inheritance": False,
    }

    metric_type = PlainReferenceField(MetricType)
    is_active = BooleanField(default=True)
    low_error = FloatField(required=False)
    low_warn = FloatField(required=False)
    high_warn = FloatField(required=False)
    high_error = FloatField(required=False)

    def __unicode__(self):
        return self.metric_type.name
