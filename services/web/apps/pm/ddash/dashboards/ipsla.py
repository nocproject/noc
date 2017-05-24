# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------
# IPSLA's dynamic dashboard
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""

import string
# NOC modules
from base import BaseDashboard
from sla.models.slaprobe import SLAProbe
from noc.sa.models.managedobject import ManagedObject
from jinja2 import Environment, FileSystemLoader
import json


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
        PM_TEMPLATE_PATH = "templates/ddash/"
        j2_env = Environment(loader=FileSystemLoader(PM_TEMPLATE_PATH))
        tmpl = j2_env.get_template("dash_ipsla.j2")
        data = tmpl.render(context)

        render = json.loads(data)
        return render
