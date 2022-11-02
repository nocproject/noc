# ---------------------------------------------------------------------
# sa.authprofile application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.app.extmodelapplication import ExtModelApplication
from noc.sa.models.authprofile import AuthProfile
from noc.core.translation import ugettext as _


class AuthProfileApplication(ExtModelApplication):
    """
    AuthProfile application
    """

    title = _("Auth Profile")
    menu = [_("Setup"), _("Auth Profiles")]
    model = AuthProfile
