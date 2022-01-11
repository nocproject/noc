# ---------------------------------------------------------------------
# pm.metricrule application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.pm.models.metricrule import MetricRule
from noc.core.translation import ugettext as _


class MetricRuleApplication(ExtDocApplication):
    """
    MetricType application
    """

    title = _("Metric Rule")
    menu = [_("Setup"), _("Metric Rules")]
    model = MetricRule
    query_condition = "icontains"
    query_fields = ["name", "description"]
