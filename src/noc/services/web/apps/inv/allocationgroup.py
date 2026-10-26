# ----------------------------------------------------------------------
# inv.allocationgroup application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.inv.models.allocationgroup import AllocationGroup
from noc.services.web.base.extdocapplication import ExtDocApplication


class AllocationGroupApplication(ExtDocApplication):
    """
    AllocationGroup application
    """

    title = "AllocationGroup"
    menu = [_("Setup"), _("Allocation Groups")]
    model = AllocationGroup
