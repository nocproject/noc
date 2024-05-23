# ----------------------------------------------------------------------
# Eltex.MES24xx.get_metrics
# ----------------------------------------------------------------------
# Copyright (C) 2024-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
import re

# NOC Modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics
from noc.core.mib import mib


class Script(GetMetricsScript):
    name = "Eltex.MES24xx.get_metrics"

    @metrics(
        [
            "Interface | Speed",
        ],
        access="S",  # SNMP version
        volatile=False,
    )
    def get_ifspeed(self, metrics):
        for iface in metrics:

            ifindex = iface.ifindex
            ilabels = iface.labels

            if re.search("Te", ilabels[0]):
                v = self.snmp.get(mib["IF-MIB::ifHighSpeed"], ifindex)
                self.set_metric(
                    id=("Interface | Speed", None),
                    value=v,
                    labels=ilabels,
                    type="gauge",
                    scale=1000000,
                    units="bit/s",
                )
            else:
                v = self.snmp.get(mib["IF-MIB::ifSpeed"], ifindex)
                self.set_metric(
                    id=("Interface | Speed", None),
                    value=v,
                    labels=ilabels,
                    type="gauge",
                    scale=1,
                    units="bit/s",
                )
