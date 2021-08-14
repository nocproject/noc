# ---------------------------------------------------------------------
# Link's dynamic dashboard
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict

# Third-Party modules
from mongoengine.errors import DoesNotExist

# NOC modules
from .jinja import JinjaDashboard
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.object import Object
from noc.inv.models.sensor import Sensor


class ContainerDashboard(JinjaDashboard):
    name = "container"
    template = "dash_container.j2"

    def resolve_object(self, object):
        o = Object.get_by_id(object)
        if not o:
            raise self.NotFound()
        self.container = o
        return ManagedObject.objects.filter(container=o)

    def resolve_object_data(self, object):
        cp = []
        if self.container:
            c = str(self.container.id)
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

        # Sensors
        sensor_types = defaultdict(list)
        sensor_enum = []
        for s in Sensor.objects.filter(object__in=self.container.get_nested_ids()):
            s_type = s.profile.name
            if not s.state.is_productive:
                s_type = "missed"
            if s.munits.enum and s.state.is_productive:
                sensor_enum += [{"bi_id": s.bi_id, "local_id": s.local_id, "units": s.munits}]
            sensor_types[s_type] += [
                {
                    "label": s.dashboard_label or s.label,
                    "units": s.munits,
                    "bi_id": s.bi_id,
                    "local_id": s.local_id,
                    "profile": s.profile,
                    "id": int(str(s.bi_id)[-10:]),
                }
            ]
        self.object_data["sensor_enum"] = sensor_enum
        self.object_data["sensor_types"] = sensor_types
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
            "sensor_types": self.object_data["sensor_types"],
            "container_id": self.container,
        }
