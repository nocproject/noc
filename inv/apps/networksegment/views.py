# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.networksegment application
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.inv.models.networksegment import NetworkSegment
from noc.sa.models.managedobject import ManagedObject


class NetworkSegmentApplication(ExtDocApplication):
    """
    NetworkSegment application
    """
    title = "NetworkSegment"
    menu = "Setup | Network Segments"
    model = NetworkSegment
    query_fields = ["name__icontains", "description__icontains"]

    def field_count(self, o):
        return ManagedObject.objects.filter(segment=o).count()

    @view("^(?P<id>[0-9a-f]{24})/effective_settings/$",
          access="read", api=True)
    def api_effective_settings(self, request, id):
        o = self.get_object_or_404(NetworkSegment, id=id)
        return o.effective_settings
