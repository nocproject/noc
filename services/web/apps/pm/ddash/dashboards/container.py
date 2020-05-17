# ---------------------------------------------------------------------
# Link's dynamic dashboard
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-Party modules
from mongoengine.errors import DoesNotExist

# NOC modules
from .jinja import JinjaDashboard
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.object import Object


class ContainerDashboard(JinjaDashboard):
    name = "container"
    template = "dash_container.j2"

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
                        cp.insert(0, {"id": str(o.id), "name": o.name})
                    c = o.container.id if o.container else None
                except DoesNotExist:
                    break
        self.object_data = {"container_path": cp}

        if not self.object:
            return self.object_data
        return self.object_data

    def get_context(self):
        bi_ids = []
        for o in self.object:
            bi_ids.append({"id": o.bi_id, "name": o.name})
        return {
            "bi_ids": bi_ids,
            "container_path": self.object_data["container_path"],
            "container_id": self.container,
        }
