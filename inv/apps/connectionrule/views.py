# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.connectionrule application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.inv.models import ConnectionRule
from noc.sa.interfaces.base import ListOfParameter, DocumentParameter
from noc.lib.prettyjson import to_json


class ConnectionRuleApplication(ExtDocApplication):
    """
    ConnectionRule application
    """
    title = "Connection Rules"
    menu = "Setup | Connection Rules"
    model = ConnectionRule

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
