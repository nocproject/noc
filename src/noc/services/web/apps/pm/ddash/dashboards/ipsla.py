# ---------------------------------------------------------------------
# IPSLA's dynamic dashboard
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-Party modules
from django.db.models import Q

# NOC modules
from .jinja import JinjaDashboard
from noc.sla.models.slaprobe import SLAProbe
from noc.sa.models.managedobject import ManagedObject


class IPSLADashboard(JinjaDashboard):
    name = "ipsla"
    template = "dash_ipsla.j2"

    def resolve_object(self, object):
        o = ManagedObject.objects.filter(Q(id=object) | Q(bi_id=object))[:1]
        if not o:
            raise self.NotFound()
        return o[0]

    def get_context(self):
        return {
            "device": self.str_cleanup(self.object.name),
            "ip": self.object.address,
            "device_id": self.object.id,
            "bi_id": self.object.bi_id,
            "segment": self.object.segment.id,
            "probes": [
                {
                    "label": f"{probe.profile}:{probe.target}",
                    "name": self.str_cleanup(probe.name),
                    "value": probe.bi_id,
                }
                for probe in SLAProbe.objects.filter(managed_object=self.object.id)
            ],
        }
