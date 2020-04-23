# ---------------------------------------------------------------------
# Iskratel.ESCOM.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.validators import is_ipv4, is_ipv6, is_mac
from noc.core.text import parse_table


class Script(BaseScript):
    name = "Iskratel.ESCOM.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_port = re.compile(
        r"^Device ID: (?P<device_id>\S+)\s*\n"
        r"^Port ID: (?P<port_id>\S+)\s*\n"
        r"^Capabilities: (?P<capabilities>.+)\s*\n"
        r"^System Name:(?P<system_name>.*)\n"
        r"^System description:(?P<system_description>.*)\n"
        r"^Port description:(?P<port_description>.*)\n",
        re.MULTILINE,
    )
    rx_port2 = re.compile(
        r"chassis id: (?P<device_id>\S+)\n+"
        r"^port id: (?P<port_id>\S+)\n+"
        r"^port description: (?P<port_description>.+)\n+"
        r"^system name: (?P<system_name>\S+|)\n+"
        r"^system description: (:?Device:\s+|)(?P<system_description>.+|)"
        r"[\s\S]+^system capabilities: (?P<capabilities>\S\s\S|\S+)",
        re.MULTILINE,
    )
    rx_search = re.compile(
        r"^(:?\S+\s+|\s+)(?P<iface>\S+\d+\/\d+)\s+\d+\s+(?P<port_id>[da-fA-F0-9]{4}.[da-fA-F0-9]{4}.[da-fA-F0-9]{4}|\S+)(:?\s+)(\w\s\w|\w)(:?\s)",
        re.MULTILINE,
    )
    data = {"O": 1, "r": 2, "B": 4, "W": 8, "R": 16, "T": 32, "C": 64, "S": 128}

    """
    if "O" in i[4]:
        caps += 1
    elif "r" in i[4]:
        caps += 2
    elif "B" in i[4]:
        caps += 4
    elif "W" in i[4]:
        caps += 8
    elif "R" in i[4]:
        caps += 16
    elif "T" in i[4]:
        caps += 32
    elif "D" in i[4]:
        caps += 64
    elif "H" in i[4]:
        caps += 128
    """

    def execute_l(self, res):
        r = []
        for line in res.splitlines():
            match = self.rx_search.search(line)
            if not match:
                continue
            iface = self.cli("show lldp neighbors interface %s" % match.group("iface"))
            iface_match = self.rx_port2.search(iface)
            chassis_id = iface_match.group("device_id")
            if is_ipv4(chassis_id) or is_ipv6(chassis_id):
                chassis_id_subtype = 5
            elif is_mac(chassis_id):
                chassis_id_subtype = 4
            else:
                chassis_id_subtype = 7
            port_id = iface_match.group("port_id")
            if is_ipv4(port_id) or is_ipv6(port_id):
                port_id_subtype = 4
            elif is_mac(port_id):
                port_id_subtype = 3
            else:
                port_id_subtype = 7
            caps = 0
            for c in iface_match.group("capabilities").split():
                c = c.strip()
                if c:
                    caps |= self.data[c]
            neighbor = {
                "remote_chassis_id": chassis_id,
                "remote_chassis_id_subtype": chassis_id_subtype,
                "remote_port": port_id,
                "remote_port_subtype": port_id_subtype,
                "remote_capabilities": caps,
            }
            if iface_match.group("system_name"):
                neighbor["remote_system_name"] = iface_match.group("system_name")
            if iface_match.group("system_description"):
                neighbor["remote_system_description"] = iface_match.group(
                    "system_description"
                ).strip()
            if iface_match.group("port_description"):
                neighbor["remote_port_description"] = iface_match.group("port_description").strip()
            r += [{"local_interface": match.group("iface"), "neighbors": [neighbor]}]
        return r

    def execute_n(self, res):
        r = []
        t = parse_table(res, allow_wrap=True)
        for i in t:
            chassis_id = i[1]
            if is_ipv4(chassis_id) or is_ipv6(chassis_id):
                chassis_id_subtype = 5
            elif is_mac(chassis_id):
                chassis_id_subtype = 4
            else:
                chassis_id_subtype = 7
            port_id = i[2]
            if is_ipv4(port_id) or is_ipv6(port_id):
                port_id_subtype = 4
            elif is_mac(port_id):
                port_id_subtype = 3
            else:
                port_id_subtype = 7
            caps = 0
            for c in i[4].split(","):
                c = c.strip()
                if c:
                    caps |= self.data[c]
            neighbor = {
                "remote_chassis_id": chassis_id,
                "remote_chassis_id_subtype": chassis_id_subtype,
                "remote_port": port_id,
                "remote_port_subtype": port_id_subtype,
                "remote_capabilities": caps,
            }
            if i[3]:
                neighbor["remote_system_name"] = i[3]
            try:
                v = self.cli("show lldp neighbors %s" % i[0])
                match = self.rx_port.search(v)
            except self.CLISyntaxError:
                pass
            if match:
                neighbor["remote_system_description"] = match.group("system_description").strip()
                neighbor["remote_port_description"] = match.group("port_description").strip()
            r += [{"local_interface": i[0], "neighbors": [neighbor]}]
        return r

    def execute(self):
        try:
            v = self.cli("show lldp neighbors")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        if self.is_escom_l:
            return self.execute_l(v)
        return self.execute_n(v)
