# ---------------------------------------------------------------------
# maintenance.maintenancetype application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.maintenance.models.maintenancetype import MaintenanceType
from noc.services.web.base.extdocapplication import ExtDocApplication


class MaintenanceTypeApplication(ExtDocApplication):
    """
    MaintenanceType application
    """

    title = _("Maintenance Type")
    menu = [_("Setup"), _("Maintenance Types")]
    model = MaintenanceType
