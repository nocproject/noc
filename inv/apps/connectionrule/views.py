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
from noc.main.models.collectioncache import CollectionCache


class ConnectionRuleApplication(ExtDocApplication):
    """
    ConnectionRule application
    """
    title = "Connection Rules"
    menu = "Setup | Connection Rules"
    model = ConnectionRule

    def field_is_builtin(self, o):
        return bool(CollectionCache.objects.filter(uuid=o.uuid))

    @view(url="^(?P<id>[0-9a-f]{24})/json/$", method=["GET"],
          access="read", api=True)
    def api_to_json(self, request, id):
        o = self.get_object_or_404(ConnectionRule, id=id)
        return o.to_json()

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
