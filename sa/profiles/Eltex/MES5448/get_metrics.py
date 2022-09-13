# ----------------------------------------------------------------------
# Eltex.MES5448.get_metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics


class Script(GetMetricsScript):
    name = "Eltex.MES5448.get_metrics"

    def get_sensor_name(self):
        sensors = {}
        for soid, name in self.snmp.getnext("1.3.6.1.2.1.47.1.1.1.1.7", cached=True):
            sindex = soid[len("1.3.6.1.2.1.47.1.1.1.1.7") + 1 :]
            sensors[sindex] = name
        return sensors

    @metrics(["Environment | Sensor Status"], volatile=False, access="S")  # CLI version
    def get_sensor_status_metrics(self, metrics):
        sensors = self.get_sensor_name()
        for oid, v in self.snmp.getnext("1.3.6.1.2.1.99.1.1.1.5"):
            sindex = oid[len("1.3.6.1.2.1.99.1.1.1.5") + 1 :]
            sname = sensors.get(sindex).strip().replace(" ", "_")
            if v == 2:
                v = 0
            self.set_metric(
                id=("Environment | Sensor Status", None),
                labels=("noc::sensor::State_%s" % sname),
                value=int(v),
                multi=True,
            )

    @metrics(["Environment | Temperature"], volatile=False, access="S")  # CLI version
    def get_sensor_temperature_metrics(self, metrics):
        sensors = self.get_sensor_name()
        for oid, s_type in self.snmp.getnext("1.3.6.1.2.1.99.1.1.1.1"):
            # celsius(8): temperature
            if s_type == 8:
                sindex = oid[len("1.3.6.1.2.1.99.1.1.1.1") + 1 :]
                sname = sensors.get(sindex).strip().replace(" ", "_")
                value = self.snmp.get("1.3.6.1.2.1.99.1.1.1.4.%s" % sindex)
                self.set_metric(
                    id=("Environment | Temperature", None),
                    labels=(f"noc::sensor::{sname}",),
                    value=int(value),
                    multi=True,
                    units="C",
                )
