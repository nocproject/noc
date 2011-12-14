# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.interface application
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtApplication, view
from noc.sa.models import ManagedObject
from noc.inv.models import Interface


class InterfaceAppplication(ExtApplication):
    """
    inv.interface application
    """
    title = "Interfaces"
    menu = "Interfaces"

    @view(url="^(?P<managed_object>\d+)/l1/", access="view", api=True)
    def api_l1(self, request, managed_object):
        """
        Physical interfaces
        :param managed_object:
        :return:
        """
        # Get object
        o = self.get_object_or_404(ManagedObject, id=int(managed_object))
        if not o.has_access(request.user):
            return self.response_forbidden("Permission denied")
        # Get object's interfaces
        # @todo: proper ordering
        return [
            {
                "name": i.name,
                "description": i.description,
                "mac": i.mac,
                "ifindex": i.ifindex
            } for i in
              Interface.objects.filter(managed_object=o.id,
                                       type="physical").order_by("name")
        ]
