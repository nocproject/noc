# ---------------------------------------------------------------------
# main.systemtemplate application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.main.models.systemtemplate import SystemTemplate
from noc.services.web.base.extmodelapplication import ExtModelApplication


class SystemTemplateApplication(ExtModelApplication):
    """
    SystemTemplate application
    """

    title = _("System Templates")
    menu = [_("Setup"), _("System Templates")]
    model = SystemTemplate
    query_fields = ["name__icontains"]
