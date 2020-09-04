# ---------------------------------------------------------------------
# Qtech.QFC.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics
from core.script.metrics import scale


class Script(GetMetricsScript):
    name = "Qtech.QFC.get_metrics"

    def check_oid(self):
        if self.is_lite:
            return 103
        return 102

    @metrics(["Interface | Status | Admin"], volatile=False, access="S")  # SNMP version
    def get_interface_admin_status(self, metrics):
        for metric in metrics:
            if metric.ifindex == 100:
                continue
            value = 0
            status = self.snmp.get(
                "1.3.6.1.4.1.27514.%s.0.%s.0" % (self.check_oid(), metric.ifindex)
            )
            if metric.ifindex in [5, 6, 13] and status == 1:
                value = 1
            elif metric.ifindex in [8, 9, 10] and status != -1000:
                value = 1
            elif metric.ifindex in [16, 27] and status > 0:
                value = 1
            self.set_metric(
                id=("Interface | Status | Admin", metric.path), value=value,
            )

    @metrics(["Environment | Temperature"], volatile=False, access="S")  # SNMP version
    def get_temperature(self, metrics):
        for metric in metrics:
            value = self.snmp.get(
                "1.3.6.1.4.1.27514.%s.0.%s.0" % (self.check_oid(), metric.ifindex)
            )
            self.set_metric(
                id=("Environment | Temperature", metric.path), value=value,
            )

    @metrics(["Environment | Voltage"], volatile=False, access="S")  # SNMP version
    def get_voltage(self, metrics):
        for metric in metrics:
            if self.is_lite:
                value = self.snmp.get("1.3.6.1.4.1.27514.103.0.19")
            else:
                value = self.snmp.get("1.3.6.1.4.1.27514.102.0.8")
            self.set_metric(
                id=("Environment | Voltage", metric.path), value=value, scale=scale(0.1)
            )
