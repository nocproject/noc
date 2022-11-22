# ---------------------------------------------------------------------
# main.template application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extmodelapplication import ExtModelApplication
from noc.main.models.template import Template
from noc.core.translation import ugettext as _


class TemplateApplication(ExtModelApplication):
    """
    Template application
    """

    title = _("Templates")
    menu = [_("Setup"), _("Templates")]
    model = Template
    query_fields = ["name__icontains", "subject__icontains"]
