# ---------------------------------------------------------------------
# inv.technology application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.inv.models.technology import Technology
from noc.core.translation import ugettext as _


class TechnologyApplication(ExtDocApplication):
    """
    Technology application
    """

    title = _("Technology")
    menu = [_("Setup"), _("Technologies")]
    model = Technology
    search = ["name"]

    def field_service_model__label(self, o):
        return o.service_model

    def field_client_model__label(self, o):
        return o.client_model
