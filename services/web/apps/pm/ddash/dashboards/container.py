# -*- coding: utf-8 -*-

# ---------------------------------------------------------------------
# Link's dynamic dashboard
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


import demjson

from jinja2 import Environment, FileSystemLoader
from noc.config import config
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.object import Object

# NOC modules
from base import BaseDashboard


class ContainerDashboard(BaseDashboard):
    name = "container"

    def resolve_object(self, object):
        try:
            self.container = object
            return ManagedObject.objects.filter(container=object)
        except ManagedObject.DoesNotExist:
            raise self.NotFound()

    def resolve_object_data(self, object):
        cp = []
        if self.container:
            c = self.container
            while c:
                try:
                    o = Object.objects.get(id=c)
                    # @todo: Address data
                    if o.container:
                        cp.insert(0, {
                            "id": str(o.id),
                            "name": o.name
                        })
                    c = o.container
                except Object.DoesNotExist:
                    break
        self.object_data = {
            "container_path": cp
        }

        if not self.object:
            return self.object_data
        return self.object_data

    def render(self):
        bi_ids = []
        for o in self.object:
            bi_ids.append({
                "id": o.bi_id,
                "name": o.name
            })
        context = {
            "bi_ids": bi_ids,
            "container_path": self.object_data["container_path"],
            "container_id": self.container
        }

        self.logger.info("Context with data: %s" % context)
        j2_env = Environment(loader=FileSystemLoader(config.path.pm_templates))
        tmpl = j2_env.get_template("dash_container.j2")
        data = tmpl.render(context)

        render = demjson.decode(data)
        return render
