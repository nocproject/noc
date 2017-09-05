# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# pm.metricscope application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.pm.models.metricscope import MetricScope
from noc.core.translation import ugettext as _


class MetricScopeApplication(ExtDocApplication):
    """
    MetricScope application
    """
    title = "MetricScope"
    menu = [_("Setup"), _("Metric Scopes")]
    model = MetricScope
