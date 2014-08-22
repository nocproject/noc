# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## pm.metrictype application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.pm.models.metrictype import MetricType


class MetricTypeApplication(ExtDocApplication):
    """
    MetricType application
    """
    title = "MetricType"
    menu = "Setup | Metric Types"
    model = MetricType
    query_fields = ["name", "description"]
