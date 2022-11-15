# ----------------------------------------------------------------------
# main.metricstream application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.main.models.metricstream import MetricStream
from noc.core.translation import ugettext as _


class MetricStreamApplication(ExtDocApplication):
    """
    CHPolicy application
    """

    title = "MetricStream"
    menu = [_("Setup"), _("Metric Stream")]
    model = MetricStream
