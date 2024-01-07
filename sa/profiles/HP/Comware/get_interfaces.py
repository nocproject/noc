# ---------------------------------------------------------------------
# HP.Comware.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.text import parse_kv


class Script(BaseScript):
    name = "HP.Comware.get_interfaces"
    interface = IGetInterfaces

    rx_mtu = re.compile(r"The Maximum Frame Length is (?P<mtu>\d+)")
    rx_ip = re.compile(r"Internet Address is (?P<ip>\S+) Primary")
    rx_mac = re.compile(
        r"IP (?:Packet Frame Type:|Sending Frames' Format is)\s*PKTFMT_ETHNT_2, Hardware Address(?: is|:) (?P<mac>\S+)"
    )

    rx_vlan_name = re.compile(r"^Vlan-interface(?P<vlan>\d+)?")
    rx_isis = re.compile(r"Interface:\s+(?P<iface>\S+)")
    rx_sub_default_vlan = re.compile(r"\(default vlan\),?")
    rx_parse_interface_vlan = re.compile(r"(\d+)(?:\(.+\))?")

    rx_iface_block_splitter = re.compile(r"^\s*\S+\d+(?:/\d+)+", re.MULTILINE)

    def get_isis_interfaces(self):
        r = []
        try:
            v = self.cli("display isis interface")
            for match in self.rx_isis.finditer(v):
                r += [match.group("iface")]
        except self.CLISyntaxError:
            pass
        return r

    interface_map = {
        "current state": "oper_status",
        "line protocol state": "line_status",
        "description": "description",
        "maximum transmit unit": "mtu",
        "port link-type": "port_type",
        "pvid": "pvid",
        "untagged vlan id": "untagged_vlan",
        "untagged vlan": "untagged_vlan",
        "untagged vlans": "untagged_vlan",
        "tagged vlan id": "tagged_vlans",
        "tagged vlans": "tagged_vlans",
        "vlan passing": "vlan_passing",
        "vlan permitted": "vlan_permitted",
    }

    def parse_interface_block(self, block):
        r = parse_kv(self.interface_map, block)
        if "mtu" not in r and self.rx_mtu.search(block):
            r["mtu"] = self.rx_mtu.search(block).group(1)
        if self.rx_mac.search(block):
            r["mac"] = self.rx_mac.search(block).group(1)
        ip_match = self.rx_ip.search(block)
        if ip_match:
            r["ip"] = ip_match.group(1)
        if "tagged_vlans" in r and self.rx_sub_default_vlan.search(r["tagged_vlans"]):
            r["tagged_vlans"] = r["tagged_vlans"].replace("(default vlan)", "")
        if "vlan_passing" in r and self.rx_sub_default_vlan.search(r["vlan_passing"]):
            r["vlan_passing"] = r["vlan_passing"].replace("(default vlan)", "")
        if "vlan_permitted" in r and self.rx_sub_default_vlan.search(r["vlan_permitted"]):
            r["vlan_permitted"] = r["vlan_permitted"].replace("(default vlan)", "")
        if "untagged_vlan" not in r and "pvid" in r:
            r["untagged_vlan"] = r["pvid"]
        if "untagged_vlan" in r:
            r["untagged_vlan"] = self.rx_parse_interface_vlan.match(r["untagged_vlan"]).group(1)
        return r

    def iter_block(self, v):
        for b in v.split("\n\n"):
            start = 0
            for match in self.rx_iface_block_splitter.finditer(b):
                """
                Fixed
                     0 aborts, 0 deferred, 0 collisions, 0 late collisions
                     - lost carrier, - no carrier
                                  GigabitEthernet1/3
                Current state: UP
                """
                if match.start() > 0:
                    start = match.start()
                    yield b[:start]
                    yield b[start:]
            if start:
                continue
            else:
                yield b

    def to_reuse_cli_session(self):
        if self.is_bad_release:
            return False
        return self.reuse_cli_session

    def to_keep_cli_session(self):
        if self.is_bad_release:
            return False
        return self.keep_cli_session

    def execute_cli(self, **kwargs):
        isis = self.get_isis_interfaces()

        # Get portchannels
        portchannel_members = {}
        for pc in self.scripts.get_portchannel():
            i = pc["interface"]
            t = pc["type"] == "L"
            for m in pc["members"]:
                portchannel_members[m] = (i, t)
        interfaces = {}
        v = self.cli("display interface")
        # "display interface Vlan-interface"
        # "display interface NULL"
        for block in self.iter_block(v):
            if not block:
                continue
            ifname, block = block.split(None, 1)
            # print(ifname, "\n\n", block, "\n\n")
            if ifname in interfaces:
                continue
            r = self.parse_interface_block(block)
            if not r:
                continue
            iftype = self.profile.get_interface_type(ifname)
            self.logger.info("Process interface: %s", ifname)
            o_status = r.get("oper_status", "").lower() == "up"
            a_status = False if "Administratively" in r.get("oper_status", "") else True
            name = ifname
            vlan_ids = 0
            if "." in ifname:
                ifname, vlan_ids = ifname.split(".", 1)
            else:
                interfaces[ifname] = {
                    "name": ifname,
                    "type": iftype,
                    "admin_status": a_status,
                    "oper_status": o_status,
                    "enabled_protocols": [],
                    "subinterfaces": [],
                }
                if "description" in r:
                    interfaces[ifname]["description"] = r["description"]
                if "mac" in r:
                    interfaces[ifname]["mac"] = r["mac"]
                if ifname in portchannel_members:
                    ai, is_lacp = portchannel_members[ifname]
                    interfaces[ifname]["aggregated_interface"] = ai
                    interfaces[ifname]["enabled_protocols"] += ["LACP"]
                if self.rx_vlan_name.match(ifname):
                    vlan_ids = self.rx_vlan_name.match(name).group(1)

            sub = {
                "name": name,
                "admin_status": a_status,
                "oper_status": o_status,
                "enabled_protocols": [],
                "enabled_afi": [],
            }
            if ifname in isis:
                sub["enabled_protocols"] += ["ISIS"]
            if "mac" in r:
                sub["mac"] = r["mac"]
            if "ip" in r:
                sub["enabled_afi"] += ["IPv4"]
                sub["ipv4_addresses"] = [r["ip"]]
            if vlan_ids:
                sub["vlan_ids"] = [int(vlan_ids)]
            if "port_type" in r:
                sub["enabled_afi"] += ["BRIDGE"]
                # Bridge interface
                if (
                    r["port_type"].lower() in ["access", "hybrid"]
                    and "untagged_vlan" in r
                    and "None" not in r["untagged_vlan"]
                ):
                    sub["untagged_vlan"] = int(r["untagged_vlan"])
                if (
                    r["port_type"].lower() in ["access", "hybrid"]
                    and "tagged_vlans" in r
                    and "None" not in r["tagged_vlans"]
                ):
                    sub["tagged_vlans"] = self.expand_rangelist((r["tagged_vlans"]))
                if r["port_type"].lower() == "trunk" and "vlan_permitted" in r:
                    sub["tagged_vlans"] = self.expand_rangelist(r["vlan_permitted"])
            interfaces[ifname]["subinterfaces"] += [sub]

        return [{"interfaces": list(interfaces.values())}]
