# ----------------------------------------------------------------------
# main.metricstream application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.main.models.metricstream import MetricStream
from noc.services.web.base.extdocapplication import ExtDocApplication


class MetricStreamApplication(ExtDocApplication):
    """
    CHPolicy application
    """

    title = "MetricStream"
    menu = [_("Setup"), _("Metric Stream")]
    model = MetricStream
