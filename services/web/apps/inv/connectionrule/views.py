# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# inv.connectionrule application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
from noc.inv.models.connectionrule import ConnectionRule
# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.lib.prettyjson import to_json
from noc.sa.interfaces.base import ListOfParameter, DocumentParameter


class ConnectionRuleApplication(ExtDocApplication):
    """
    ConnectionRule application
    """
    title = _("Connection Rules")
    menu = [_("Setup"), _("Connection Rules")]
    model = ConnectionRule
    query_fields = ["name__icontains", "description__icontains"]

    @view(url="^actions/json/$", method=["POST"],
          access="read",
          validate={
              "ids": ListOfParameter(element=DocumentParameter(ConnectionRule), convert=True)
          },
          api=True)
    def api_action_json(self, request, ids):
        r = [o.json_data for o in ids]
        s = to_json(r, order=["name", "description"])
        return {"data": s}
