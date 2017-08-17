# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------
# Link's dynamic dashboard
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""

import json

from jinja2 import Environment, FileSystemLoader
from noc.config import config
from noc.inv.models.link import Link

# NOC modules
from base import BaseDashboard


class LinkDashboard(BaseDashboard):
    name = "link"

    def resolve_object(self, object):
        try:
            return Link.objects.get(id=object)
        except Link.DoesNotExist:
            raise self.NotFound()

    def render(self):
        mos = self.object
        if mos.interfaces[0].description:
            mos.interfaces[0].description = mos.interfaces[0].description.replace('\"', '')
        if mos.interfaces[1].description:
            mos.interfaces[1].description = mos.interfaces[1].description.replace('\"', '')
        context = {
            "device_a": mos.interfaces[0].managed_object.name.replace('\"', ''),
            "device_b": mos.interfaces[1].managed_object.name.replace('\"', ''),
            "bi_id_a": mos.interfaces[0].managed_object.get_bi_id(),
            "bi_id_b": mos.interfaces[0].managed_object.get_bi_id(),
            "interface_a": {
                "name": mos.interfaces[0].name,
                "descr": mos.interfaces[0].description or mos.interfaces[0].name},
            "interface_b": {
                "name": mos.interfaces[1].name,
                "descr": mos.interfaces[1].description or mos.interfaces[1].name},
            "segment": mos.managed_objects[0].segment.id,
            "device_a_id": mos.managed_objects[0].id,
            "device_b_id": mos.managed_objects[1].id,
            "pool": mos.managed_objects[0].pool.name,
            "link_id": mos.id
        }
        self.logger.info("Context with data: %s" % context)
        j2_env = Environment(loader=FileSystemLoader(config.path.pm_templates))
        tmpl = j2_env.get_template("dash_link.j2")
        data = tmpl.render(context)

        render = json.loads(data)
        return render
