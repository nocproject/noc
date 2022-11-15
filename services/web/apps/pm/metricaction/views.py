# ---------------------------------------------------------------------
# pm.metricrule application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.pm.models.metricaction import MetricAction
from noc.core.translation import ugettext as _


class MetricActionApplication(ExtDocApplication):
    """
    MetricType application
    """

    title = _("Metric Action")
    menu = [_("Setup"), _("Metric Actions")]
    model = MetricAction
    query_condition = "icontains"
    query_fields = ["name", "description"]
