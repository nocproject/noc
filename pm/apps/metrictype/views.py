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
from noc.main.models.doccategory import DocCategory


class MetricTypeApplication(ExtDocApplication):
    """
    MetricType application
    """
    title = "Metric Type"
    menu = "Setup | Metric Types"
    model = MetricType
    parent_model = DocCategory
    parent_field = "parent"
    query_fields = ["name", "description"]
