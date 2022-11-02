# ---------------------------------------------------------------------
# sa.useraccess application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.app.extmodelapplication import ExtModelApplication
from noc.sa.models.useraccess import UserAccess
from noc.core.translation import ugettext as _


class UserAccessApplication(ExtModelApplication):
    """
    UserAccess application
    """

    title = _("User Access")
    menu = [_("Setup"), _("User Access")]
    model = UserAccess
