# ----------------------------------------------------------------------
# pm.scale application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.pm.models.scale import Scale
from noc.services.web.base.extdocapplication import ExtDocApplication


class ScaleApplication(ExtDocApplication):
    """
    Scale application
    """

    title = "Scale"
    menu = [_("Setup"), _("Scale")]
    model = Scale
    query_condition = "icontains"
    query_fields = ["name", "description"]
