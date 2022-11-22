# ---------------------------------------------------------------------
# main.resourcestate application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extmodelapplication import ExtModelApplication
from noc.main.models.resourcestate import ResourceState
from noc.core.translation import ugettext as _


class ResourceStateApplication(ExtModelApplication):
    """
    ResourceState application
    """

    title = _("Resource States")
    menu = [_("Setup"), _("Resource States")]
    model = ResourceState
    query_fields = ["name", "description"]
    query_condition = "icontains"
