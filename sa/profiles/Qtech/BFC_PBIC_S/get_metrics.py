# ---------------------------------------------------------------------
# Qtech.BFC_PBIC_S.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics
from core.script.metrics import scale


class Script(GetMetricsScript):
    name = "Qtech.BFC_PBIC_S.get_metrics"

    @metrics(["Interface | Status | Admin"], volatile=False, access="S")  # SNMP version
    def get_interface_admin_status(self, metrics):
        for metric in metrics:
            value = 0
            descr = self.snmp.get("1.3.6.1.3.55.1.3.1.2.%s" % metric.ifindex)
            status = self.snmp.get("1.3.6.1.3.55.1.3.1.4.%s" % metric.ifindex)
            invert = self.snmp.get("1.3.6.1.3.55.1.3.1.3.%s" % metric.ifindex)
            if descr in [0, 3, 9, 10]:
                if invert == 0 and status == 0:
                    value = 1
                elif invert == 1 and status == 1:
                    value = 1
            else:
                if status > 0:
                    value = 1
            if len(metric.ifindex) == 2:
                ifindes = list(str(metric.ifindex))
                temp = self.snmp.get(
                    "1.3.6.1.3.55.1.%s.%s.0" % (ifindes[0], ifindes[1]), cached=True
                )
                if temp != -104:
                    value = 1
            self.set_metric(
                id=("Interface | Status | Admin", metric.path), value=value,
            )

    @metrics(["Environment | Temperature"], volatile=False, access="S")  # SNMP version
    def get_temperature(self, metrics):
        for metric in metrics:
            ifindes = list(str(metric.ifindex))
            temp = self.snmp.get("1.3.6.1.3.55.1.%s.%s.0" % (ifindes[0], ifindes[1]), cached=True)
            self.set_metric(
                id=("Environment | Temperature", metric.path), value=temp,
            )

    @metrics(["Environment | Voltage"], volatile=False, access="S")  # SNMP version
    def get_voltage(self, metrics):
        for metric in metrics:
            value = self.snmp.get("1.3.6.1.3.55.1.3.1.4.%s" % metric.ifindex)
            self.set_metric(
                id=("Environment | Voltage", metric.path), value=value, scale=scale(0.001)
            )
