# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ip.ippool application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication
from noc.ip.models.ippool import IPPool
from noc.inv.models.technology import Technology
from noc.sa.interfaces.base import InterfaceTypeError
from noc.core.translation import ugettext as _


class IPPoolApplication(ExtModelApplication):
    """
    IPPool application
    """
    title = _("IP Pool")
    menu = [_("Setup"), _("IP Pools")]
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
            if not Technology.objects.filter(name="Packet | %s" % t).count():
                raise InterfaceTypeError("Invalid technology: '%s'" % t)
        data["technologies"] = technologies
        return super(IPPoolApplication, self).clean(data)
