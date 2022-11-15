# ---------------------------------------------------------------------
# project.project application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extmodelapplication import ExtModelApplication
from noc.project.models.project import Project
from noc.core.translation import ugettext as _


class ProjectApplication(ExtModelApplication):
    """
    Project application
    """

    title = _("Project")
    menu = _("Projects")
    model = Project
    query_condition = "icontains"
    query_fields = ["code", "name", "description"]
