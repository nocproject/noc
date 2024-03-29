# ---------------------------------------------------------------------
# pm.metrictype application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.pm.models.metrictype import MetricType
from noc.main.models.doccategory import DocCategory
from noc.core.translation import ugettext as _


class MetricTypeApplication(ExtDocApplication):
    """
    MetricType application
    """

    title = _("Metric Type")
    menu = [_("Setup"), _("Metric Types")]
    model = MetricType
    parent_model = DocCategory
    parent_field = "parent"
    query_condition = "icontains"
    query_fields = ["name", "description"]
