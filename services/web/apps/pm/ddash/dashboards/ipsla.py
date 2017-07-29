# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------
# IPSLA's dynamic dashboard
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""

import json

from jinja2 import Environment, FileSystemLoader
from noc.config import config
from noc.sa.models.managedobject import ManagedObject

# NOC modules
from base import BaseDashboard
from sla.models.slaprobe import SLAProbe


class IPSLADashboard(BaseDashboard):
    name = "ipsla"

    def resolve_object(self, object):
        try:
            return ManagedObject.objects.get(id=object)
        except ManagedObject.DoesNotExist:
            raise self.NotFound()

    def render(self):
        context = {
            "device": self.object.name.replace('\"', ''),
            "ip": self.object.address,
            "device_id": self.object.id,
            "segment": self.object.segment.id,
            "probes": [{"name": probe.name.replace('\"', ''), "value": probe.tests[0].target} for
                       probe in SLAProbe.objects.filter(managed_object=self.object.id)]
        }
        self.logger.info("Context with data: %s" % context)
        j2_env = Environment(loader=FileSystemLoader(config.path.pm_templates))
        tmpl = j2_env.get_template("dash_ipsla.j2")
        data = tmpl.render(context)

        render = json.loads(data)
        return render
