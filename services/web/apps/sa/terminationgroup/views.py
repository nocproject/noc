# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# sa.terminationgroup application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication, view
from noc.lib.app.modelinline import ModelInline
from noc.sa.models.terminationgroup import TerminationGroup
from noc.ip.models.ippool import IPPool
from noc.inv.models.technology import Technology
from noc.sa.interfaces.base import InterfaceTypeError
from noc.core.translation import ugettext as _


class IPPoolInline(ModelInline):
    def clean(self, data, parent):
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
        return super(IPPoolInline, self).clean(data, parent)


class TerminationGroupApplication(ExtModelApplication):
    """
    TerminationGroup application
    """
    title = _("Termination Group")
    menu = [_("Setup"), _("Termination Groups")]
    model = TerminationGroup
    query_fields = ["name__icontains"]
    ippool = IPPoolInline(IPPool)

    def field_terminators(self, o):
        return [m.name for m in o.termination_set.all()]

    def field_n_access(self, o):
        return o.access_set.count()
