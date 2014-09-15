## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MetricItem model
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import (StringField, BooleanField,
                                FloatField, ReferenceField)
## NOC Modules
from metrictype import MetricType


class MetricItem(EmbeddedDocument):
    meta = {
        "allow_inheritance": False,
    }

    metric_type = ReferenceField(MetricType)
    is_active = BooleanField(default=True)
    # Optional graphite metric name
    metric = StringField(required=False)
    low_error = FloatField(required=False)
    low_warn = FloatField(required=False)
    high_warn = FloatField(required=False)
    high_error = FloatField(required=False)

    def __unicode__(self):
        return self.metric_type.name
