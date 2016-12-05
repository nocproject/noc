# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## sla.slaprobe application
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.sla.models.slaprobe import SLAProbe
from noc.core.translation import ugettext as _


class SLAProbeApplication(ExtDocApplication):
    """
    SLAProbe application
    """
    title = "SLA Probe"
    menu = _("SLA Probes")
    model = SLAProbe

    def field_row_class(self, o):
        return o.profile.style.css_class_name if o.profile and o.profile.style else ""

    def field_targets(self, o):
        r = []
        for t in o.tests:
            if t.target:
                r += ["%s:%s" % (t.type, t.target)]
        return ", ".join(r)
