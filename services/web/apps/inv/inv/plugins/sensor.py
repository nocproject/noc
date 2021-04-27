# ---------------------------------------------------------------------
# inv.inv sensor plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from .base import InvPlugin
from noc.inv.models.sensor import Sensor
from noc.inv.models.sensorprofile import SensorProfile
from noc.pm.models.measurementunits import MeasurementUnits
from noc.sa.interfaces.base import ObjectIdParameter


class SensorPlugin(InvPlugin):
    name = "sensor"
    js = "NOC.inv.inv.plugins.sensor.SensorPanel"

    def get_data(self, request, o: "Sensor"):
        return [
            {
                "profile__label": s.profile.name,
                "profile": str(s.profile.id),
                "object__label": s.object.name,
                "object": str(s.object.id),
                "local_id": s.local_id,
                "state__label": s.state.name,
                "state": str(s.state.id),
                "units__label": s.units.name,
                "units": str(s.units.id),
                "label": s.label,
                "dashboard_label": None,
                "protocol": s.protocol,
                "modbus_register": s.modbus_register,
                "snmp_oid": s.snmp_oid or None,
                "bi_id": str(s.bi_id),
                "id": str(s.id),
            }
            for s in Sensor.objects.filter(object=o.id)
        ]

    def init_plugin(self):
        super().init_plugin()
        self.add_view(
            "api_plugin_%s_set_sensor" % self.name,
            self.api_set_sensor,
            url="^(?P<id>[0-9a-f]{24})/plugin/%s/$" % self.name,
            method=["POST"],
            validate={
                "profile": ObjectIdParameter(required=False),
                "units": ObjectIdParameter(required=False),
            },
        )

    def api_set_sensor(self, request, id, profile=None, units=None):
        s = self.app.get_object_or_404(Sensor, id=id)
        if profile:
            sp = SensorProfile.get_by_id(profile)
            s.profile = sp
        if units:
            u = MeasurementUnits.get_by_id(units)
            s.units = u
        s.save()
        return {"success": True}
