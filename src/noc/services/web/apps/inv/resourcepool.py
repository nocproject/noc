# ----------------------------------------------------------------------
# inv.resourcepool application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.inv.models.resourcepool import ResourcePool
from noc.services.web.base.extdocapplication import ExtDocApplication


class ResourcePoolApplication(ExtDocApplication):
    """
    ResourcePool application
    """

    title = "ResourcePool"
    menu = [_("Setup"), _("Resource Pool")]
    model = ResourcePool
