# ---------------------------------------------------------------------
# Huawei.VRP.get_dom_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetdomstatus import IGetDOMStatus
from noc.core.text import parse_table, parse_kv


class Script(BaseScript):
    name = "Huawei.VRP.get_dom_status"
    interface = IGetDOMStatus

    rx_port = re.compile(r"Port (?P<port>\S+\d+) transceiver diagnostic information:")

    ne_map = {"tx power": "tx_power", "rx power": "rx_power"}
    ar_map = {
        "current tx power(dbm)": "tx_power",
        "current rx power(dbm)": "rx_power",
        "bias current(ma)": "current",
        "temperature()": "temp",
        "voltage(v)": "voltage",
    }

    def parse_ports(self, s):
        match = self.rx_port.search(s)
        if match:
            port = match.group("port")
            obj = match.groupdict()
            return port, obj, s[match.end() :]
        return None

    def execute_ne(self, interface=None):
        """
        NE series
        GigabitEthernet0/3/4
        Port Physical Status : UP
        Physical Down Reason : none
        Loopback             : none
        Duplex mode          : full-duplex
        negotiation          : enable
        Pause Flowcontrol    : Receive Enable and Send Enable
        SFP imformation:
        The Vendor PN is SFP-WDM57.36
        The Vendor Name is OptiCin, Port BW: 1G, Transceiver BW: 1G, Transceiver Mode: SingleMode
        WaveLength: 1570nm, Transmission Distance: 140km
        Rx Power: -31.54dBm, Warning range: [-33.979,  -9.003]dBm
        Tx Power:   3.03dBm, Warning range: [1.999,  6.999]dBm
        :param interface:
        :return:
        """
        cmd = "display interface phy-option"
        if interface is not None:
            cmd += " %s" % interface
        try:
            c = self.cli(cmd)
        except self.CLISyntaxError:
            return []
        r = []
        for block in c.split("\n\n"):
            if not block.strip() or "transceiver offline" in block:
                continue
            iface = {"interface": block.splitlines()[0]}
            res = parse_kv(self.ne_map, block)
            if "rx_power" in res:
                # Rx Power: -10.44dBm, Warning range: [-17.011,  0.000]dBm
                iface["optical_rx_dbm"] = float(res["rx_power"].split(",")[0][:-3])
            if "tx_power" in res:
                # Tx Power:   3.35dBm, Warning range: [0.999,  5.000]dBm
                iface["optical_tx_dbm"] = float(res["tx_power"].split(",")[0][:-3])
            if len(iface) == 1:
                # No metrics
                continue
            r += [iface]
        return r

    def execute_ar(self, interface=None):
        """
        AR Series
        GigabitEthernet0/0/0 information:
        -------------------------------------------------------------
        Electronic label information:
          Description               :1300Mb/sec-1570nm-SC-SM-140km(0.009mm)
          Type                      :SFP-WDM57.36
          Manufacturer              :OptiCin
          HuaweiPartNumber          :
        -------------------------------------------------------------
        Alarm information:
          SFP Module Authentication Fail
        -------------------------------------------------------------
        Realtime information:
          Temperature(Ўж)                          :42
          Temperature High Threshold(Ўж)           :95
          Temperature Low  Threshold(Ўж)           :-42
          Voltage(V)                               :3.25
          Voltage High Threshold(V)                :3.50
          Voltage Low  Threshold(V)                :3.05
          Bias Current(mA)                         :35.46
          Bias High Threshold(mA)                  :80.00
          Bias Low  Threshold(mA)                  :3.00
          Current Rx Power(dBM)                    :-22.03
          Default Rx Power High Threshold(dBM)     :-8.99
          Default Rx Power Low  Threshold(dBM)     :-33.97
          Current Tx Power(dBM)                    :2.95
          Default Tx Power High Threshold(dBM)     :6.99
          Default Tx Power Low  Threshold(dBM)     :2.00
          User Set Rx Power High Threshold(dBM)    :-8.99
          User Set Rx Power Low Threshold(dBM)     :-33.97
          User Set Tx Power High Threshold(dBM)    :6.99
          User Set Tx Power Low Threshold(dBM)     :2.00
        -------------------------------------------------------------
        :param interface:
        :return:
        """
        cmd = "dis transceiver verbose"
        if interface is not None:
            cmd = "dis transceiver interface %s verbose" % interface
        try:
            c = self.cli(cmd)
        except self.CLISyntaxError:
            return []

        r = []
        for block in c.strip("\n\r").split("\n\n"):
            if not block.strip() or "Realtime information:" not in block:
                continue
            iface = {"interface": block.splitlines()[0].split("information")[0].strip()}
            res = parse_kv(self.ar_map, block)
            if "rx_power" in res:
                # Rx Power: -10.44dBm, Warning range: [-17.011,  0.000]dBm
                iface["optical_rx_dbm"] = float(res["rx_power"])
            if "tx_power" in res:
                # Tx Power:   3.35dBm, Warning range: [0.999,  5.000]dBm
                iface["optical_tx_dbm"] = float(res["tx_power"])
            if "current" in res:
                # Tx Power:   3.35dBm, Warning range: [0.999,  5.000]dBm
                iface["current_ma"] = float(res["current"])
            if "temp" in res:
                # Tx Power:   3.35dBm, Warning range: [0.999,  5.000]dBm
                iface["temp_c"] = float(res["temp"])
            if "voltage" in res:
                # Tx Power:   3.35dBm, Warning range: [0.999,  5.000]dBm
                iface["voltage_v"] = float(res["voltage"])
            if len(iface) == 1:
                # No metrics
                self.logger.info("No metrics for iface %s", iface)
                continue
            r += [iface]

        return r

    def execute(self, interface=None):
        if self.is_ne_platform or self.is_cx600:
            return self.execute_ne(interface=interface)
        if self.is_ar:
            return self.execute_ar(interface=interface)
        cmd = "display transceiver diagnosis interface"
        if interface is not None:
            cmd += " %s" % interface
        try:
            c = self.cli(cmd)
        except self.CLISyntaxError:
            return []

        r = []
        for block in c.split("\n\n"):
            match = self.rx_port.search(block)
            if match:
                iface = {"interface": match.group("port")}
                t = parse_table(block)
                for i in t:
                    if i[0] == "TxPower(dBm)":
                        iface["optical_tx_dbm"] = i[1]
                    if i[0] == "RxPower(dBm)":
                        iface["optical_rx_dbm"] = i[1]
                    if i[0] == "Current(mA)":
                        iface["current_ma"] = i[1]
                    if i[0] == "Temp.(C)":
                        iface["temp_c"] = i[1]
                    if i[0] == "Voltage(V)":
                        iface["voltage_v"] = i[1]
                if t:
                    r += [iface]
        return r
