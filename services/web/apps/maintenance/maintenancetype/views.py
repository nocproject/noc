# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# maintenance.maintenancetype application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.maintenance.models.maintenancetype import MaintenanceType
from noc.core.translation import ugettext as _


class MaintenanceTypeApplication(ExtDocApplication):
    """
    MaintenanceType application
    """
    title = _("Maintenance Type")
    menu = [_("Setup"), _("Maintenance Types")]
    model = MaintenanceType
