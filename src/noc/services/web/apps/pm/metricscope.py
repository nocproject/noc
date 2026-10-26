# ----------------------------------------------------------------------
# pm.metricscope application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.pm.models.metricscope import MetricScope
from noc.services.web.base.extdocapplication import ExtDocApplication


class MetricScopeApplication(ExtDocApplication):
    """
    MetricScope application
    """

    title = "MetricScope"
    menu = [_("Setup"), _("Metric Scopes")]
    model = MetricScope
