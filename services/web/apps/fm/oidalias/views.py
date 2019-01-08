# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# fm.oidalias application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.fm.models.oidalias import OIDAlias
from noc.core.translation import ugettext as _


class OIDAliasApplication(ExtDocApplication):
    """
    OIDAlias application
    """
    title = _("OID Aliases")
    menu = [_("Setup"), _("OID Aliases")]
    model = OIDAlias

    @view(url="^(?P<id>[0-9a-f]{24})/json/$", method=["GET"],
          access="read", api=True)
    def api_json(self, request, id):
        oa = self.get_object_or_404(OIDAlias, id=id)
        return oa.to_json()
