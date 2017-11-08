# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# maintenance.maintenancetype application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.maintenance.models.maintenancetype import MaintenanceType


class MaintenanceTypeApplication(ExtDocApplication):
    """
    MaintenanceType application
    """
    title = _("Maintenance Type")
    menu = [_("Setup"), _("Maintenance Types")]
    model = MaintenanceType
