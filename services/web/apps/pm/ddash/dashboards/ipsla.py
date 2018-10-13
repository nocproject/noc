# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IPSLA's dynamic dashboard
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-Party modules
import demjson
from django.db.models import Q
from jinja2 import Environment, FileSystemLoader
# NOC modules
from .base import BaseDashboard
from sla.models.slaprobe import SLAProbe
from noc.config import config
from noc.sa.models.managedobject import ManagedObject


class IPSLADashboard(BaseDashboard):
    name = "ipsla"

    def resolve_object(self, object):
        o = ManagedObject.objects.filter(Q(id=object) | Q(bi_id=object))[:1]
        if not o:
            raise self.NotFound()
        else:
            return o[0]

    def render(self):
        context = {
            "device": self.str_cleanup(self.object.name),
            "ip": self.object.address,
            "device_id": self.object.id,
            "bi_id": self.object.bi_id,
            "segment": self.object.segment.id,
            "probes": [{"name": self.str_cleanup(probe.name), "value": probe.target} for
                       probe in SLAProbe.objects.filter(managed_object=self.object.id)]
        }
        self.logger.info("Context with data: %s" % context)
        j2_env = Environment(loader=FileSystemLoader(config.path.pm_templates))
        tmpl = j2_env.get_template("dash_ipsla.j2")
        data = tmpl.render(context)

        render = demjson.decode(data)
        return render
