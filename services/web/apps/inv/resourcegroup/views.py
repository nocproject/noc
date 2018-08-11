# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# inv.resourcegroup application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.inv.models.resourcegroup import ResourceGroup
from noc.core.translation import ugettext as _


class ResourceGroupApplication(ExtDocApplication):
    """
    ResourceGroup application
    """
    title = "ResourceGroup"
    menu = [_("Setup"), _("Resource Groups")]
    model = ResourceGroup
