# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ip.ippool application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.ip.models import IPPool
from noc.inv.models.technology import Technology
from noc.sa.interfaces.base import InterfaceTypeError


class IPPoolApplication(ExtModelApplication):
    """
    IPPool application
    """
    title = "IP Pool"
    menu = "Setup | IP Pools"
    model = IPPool

    def clean(self, data):
        technologies = data.get("technologies", ["IPoE"])
        if isinstance(technologies, (str, unicode)):
            technologies = [s.strip() for s in technologies.split(",") if s.strip()]
            if not technologies:
                technologies = ["IPoE"]
        # Normalize technologies
        for t in technologies:
            if "|" in t:
                raise InterfaceTypeError("Invalid technology: '%s'" % t)
            if not Technology.objects.filter(name = "Packet | %s" % t).count():
                raise InterfaceTypeError("Invalid technology: '%s'" % t)
        data["technologies"] = technologies
        return super(IPPoolApplication, self).clean(data)