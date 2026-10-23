# ---------------------------------------------------------------------
# inv.connectionrule application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.http import HttpRequest

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, api
from noc.inv.models.connectionrule import ConnectionRule
from noc.sa.interfaces.base import ListOfParameter, DocumentParameter
from noc.core.prettyjson import to_json
from noc.core.translation import ugettext as _


class ConnectionRuleApplication(ExtDocApplication):
    """
    ConnectionRule application
    """

    title = _("Connection Rules")
    menu = [_("Setup"), _("Connection Rules")]
    model = ConnectionRule
    query_fields = ["name__icontains", "description__icontains"]

    @api.post(
        "^actions/json/$",
        access="read",
        validate={"ids": ListOfParameter(element=DocumentParameter(ConnectionRule), convert=True)},
    )
    def api_action_json(self, request: HttpRequest, ids):
        r = [o.json_data for o in ids]
        s = to_json(r, order=["name", "description"])
        return {"data": s}
