# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.connectiontype application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.inv.models.connectiontype import ConnectionType


class ConnectionTypeApplication(ExtDocApplication):
    """
    ConnectionType application
    """
    title = "Connection Types"
    menu = "Setup | Connection Types"
    model = ConnectionType
    query_fields = ["name__icontains", "description__icontains"]

    @view(url="^(?P<id>[0-9a-f]{24})/json/$", method=["GET"],
          access="read", api=True)
    def api_to_json(self, request, id):
        o = self.get_object_or_404(ConnectionType, id=id)
        return o.to_json()
