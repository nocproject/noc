# ---------------------------------------------------------------------
# sla.slaprobe application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.sla.models.slaprobe import SLAProbe
from noc.services.web.base.decorators.state import state_handler
from noc.core.translation import ugettext as _


@state_handler
class SLAProbeApplication(ExtDocApplication):
    """
    SLAProbe application
    """

    title = "SLA Probe"
    menu = _("SLA Probes")
    query_fields = ["name__icontains", "target__icontains", "description__icontains"]
    model = SLAProbe

    def field_targets(self, o):
        return ", ".join([f"{o.type}:{o.target}"])

    def field_target_id(self, o):
        t = o.get_target()
        if t:
            return t.id
        return None
