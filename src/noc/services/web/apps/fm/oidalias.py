# ---------------------------------------------------------------------
# fm.oidalias application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.http import HttpRequest

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, api
from noc.fm.models.oidalias import OIDAlias
from noc.core.translation import ugettext as _


class OIDAliasApplication(ExtDocApplication):
    """
    OIDAlias application
    """

    title = _("OID Aliases")
    menu = [_("Setup"), _("OID Aliases")]
    model = OIDAlias

    @api.get("^(?P<id>[0-9a-f]{24})/json/$", access="read")
    def api_json(self, request: HttpRequest, id):
        oa = self.get_object_or_404(OIDAlias, id=id)
        return oa.to_json()
