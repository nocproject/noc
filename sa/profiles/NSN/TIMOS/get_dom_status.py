# ---------------------------------------------------------------------
# NSN.TIMOS..get_dom_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetdomstatus import IGetDOMStatus


class Script(BaseScript):
    name = "NSN.TIMOS.get_dom_status"
    interface = IGetDOMStatus

    def execute_snmp(self, interface=None, **kwargs):
        r = []
        names = {v: k for k, v in self.scripts.get_ifindexes(name_oid="IF-MIB::ifName").items()}
        for (
            index,
            temp_c,
            voltage_v,
            current_ma,
            optical_tx_dbm,
            optical_rx_dbm,
        ) in self.snmp.get_tables(
            [
                "1.3.6.1.4.1.6527.3.1.2.2.4.31.1.1",
                "1.3.6.1.4.1.6527.3.1.2.2.4.31.1.6",
                "1.3.6.1.4.1.6527.3.1.2.2.4.31.1.11",
                "1.3.6.1.4.1.6527.3.1.2.2.4.31.1.16",
                "1.3.6.1.4.1.6527.3.1.2.2.4.31.1.21",
            ],
            bulk=False,
        ):
            if temp_c == 2147483647:
                continue
            iface_index = index.rsplit(".", 1)[-1]
            r += [
                {
                    "interface": names[int(iface_index)],
                    "temp_c": float(temp_c) / 256,
                    "voltage_v": float(voltage_v) / 1000,
                    "current_ma": float(current_ma) / 500,
                    "optical_tx_dbm": float(optical_tx_dbm) / 100.0,
                    "optical_rx_dbm": (
                        float(optical_rx_dbm) / 100.0 if optical_rx_dbm != 2147483647 else 0
                    ),
                }
            ]
        return r
