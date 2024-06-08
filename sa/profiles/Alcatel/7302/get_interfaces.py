# ----------------------------------------------------------------------
# Alcatel.7302.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
from collections import defaultdict
from itertools import chain
from typing import Tuple

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4
from noc.core.mib import mib
from noc.core.text import parse_table


class Script(BaseScript):
    name = "Alcatel.7302.get_interfaces"
    interface = IGetInterfaces

    rx_bridge_port = re.compile(
        r"^(?P<ifname>\S+)\s+(?P<bridge_port>\d+)\s+(?P<pvid>\d+)\s+\d+\s*\n", re.MULTILINE
    )
    rx_bridge_port2 = re.compile(
        r"^port (?P<ifname>\S+)\s*\n(^\s+.+\n)+?^\s+pvid (?P<pvid>\d+)\s*\n^exit",
        re.MULTILINE,
    )
    rx_uplink_port = re.compile(
        r"^(?P<port>\d+)\s+(?P<admin_status>up|down)\s+(?P<oper_status>up|down)", re.MULTILINE
    )
    rx_vlan_map = re.compile(r"^(?P<ifname>\S+)\s+(?P<vlan_id>\d+)\s*\n", re.MULTILINE)
    rx_ifname = re.compile(r"port : (?P<ifname>\S+)")
    rx_ifindex = re.compile(r"if-index : (?P<ifindex>\d+)")
    rx_ififo = re.compile(r'info : "(?P<info>.+?)"')
    rx_type = re.compile(r"type : (?P<type>\S+)")
    rx_mac = re.compile(r"phy-addr : (?P<mac>\S+)")
    rx_admin_status = re.compile(
        r"admin-status : (?P<admin_status>up|admin-up|down|admin-down|not-appl)"
    )
    rx_oper_status = re.compile(r"opr-status : (?P<oper_status>up|down|no-value)")
    rx_mtu = re.compile(r"largest-pkt-size : (?P<mtu>\d+)")
    rx_vpi_vci = re.compile(r"(?P<ifname>\S+\d+):(?P<vpi>\d+):(?P<vci>\d+)")
    rx_ip = re.compile(
        r"^(?P<iface>\d+)\s+(?P<vlan_id>\d+)\s+(?P<admin_status>up|down)\s+"
        r"(?P<oper_status>up|down)\s+(?P<ip>\d\S+)\s+(?P<mask>\d\S+)",
        re.MULTILINE,
    )
    rx_mgmt_ip = re.compile(r"host-ip-address manual:(?P<ip>\d+\.\d+\.\d+\.\d+\/\d+)")
    rx_mgmt_vlan = re.compile(r"mgnt-vlan-id (?P<vlan_id>\d+)")
    rx_mgmt_ip2 = re.compile(
        r"configure system management(?: vlan (?P<vlan_id>\d+))? "
        r"host-ip-address manual:(?P<ip>\d+\.\d+\.\d+\.\d+\/\d+)"
    )
    types = {
        "ethernet": "physical",
        "slip": "tunnel",
        "xdsl-line": "physical",
        "xdsl-channel": "other",
        "atm-bonding": "other",
        "atm": "other",
        "atm-ima": "other",
        "efm": "other",
        "shdsl": "physical",
        "l2-vlan": "other",
        "sw-loopback": "loopback",
        "bonding": "other",
        "bridge-port": "other",
    }

    PROCCESSED_TYPE = {
        6: {"type": "physical"},  # ethernetCsmacd
        24: {"type": "loopback", "prefix": "sw-loopback"},  # softwareLoopback
        238: {"type": "physical"},  # aluELP (adsl2plus)
        249: {"type": "physical"},  # aluELP (xdsl-line)
    }

    avail_status_map = {
        1: "available",
        2: "inTest",
        3: "failed",
        4: "powerOff",
        5: "notInstalled",
        6: "offLine",
        7: "dependency",
    }

    collected_slots_status = {"available", "inTest", "failed", "powerOff"}

    def get_boards_status_cli(self):
        r = {}
        v = self.cli("show equipment slot", cached=True)
        for p in parse_table(v):
            if not p[0].startswith("lt"):
                continue
            slot_id = p[0].split(":", 1)[-1]
            r[tuple(slot_id.split("/"))] = p[4] in self.collected_slots_status
        return r

    def get_subifaces_cli(self):
        sub = defaultdict(list)
        v = ""
        try:
            v = self.cli("show bridge port")
        except self.CLISyntaxError:
            pass
        except self.CLIOperationError:
            raise NotImplementedError("Internal processing error")
        for match in self.rx_bridge_port.finditer(v):
            ifname = match.group("ifname")
            if ":" not in ifname:
                continue
            if ifname.startswith("isam:"):
                _, port_id, vpi, vci = ifname.split(":")
            else:
                port_id, vpi, vci = ifname.split(":")
            sub[port_id] += [
                {
                    "name": f"{port_id}:{vpi}:{vci}",
                    "vci": vci,
                    "vpi": vpi,
                    # "snmp_ifindex": vciifindex,
                    "enabled_afi": ["ATM", "BRIDGE"],
                    "untagged_vlan": match.group("pvid"),
                }
            ]

        if not sub:
            v = self.cli("info configure bridge port")
            for match in self.rx_bridge_port2.finditer(v):
                ifname = match.group("ifname")
                if ":" not in ifname:
                    continue
                if ifname.startswith("isam:"):
                    _, port_id, vpi, vci = ifname.split(":")
                else:
                    port_id, vpi, vci = ifname.split(":")
                sub[port_id] += [
                    {
                        "name": f"{port_id}:{vpi}:{vci}",
                        "vci": vci,
                        "vpi": vpi,
                        # "snmp_ifindex": vciifindex,
                        "enabled_afi": ["ATM", "BRIDGE"],
                        "untagged_vlan": match.group("pvid"),
                    }
                ]
        return sub

    def execute_cli(self, **kwargs):
        self.cli(
            "environment inhibit-alarms mode batch terminal-timeout timeout:360", ignore_errors=True
        )
        subifaces = self.get_subifaces_cli()
        tagged_vlans = {}
        v = self.cli("show vlan shub-port-vlan-map", cached=True)
        for match in self.rx_vlan_map.finditer(v):
            ifname = match.group("ifname")
            ifname = ifname.replace("lt:", "atm-if:")
            if ifname == "network:0":
                ifname = "ethernet:0"
            if ifname == "network:1":
                ifname = "ethernet:1"
            if ifname == "network:2":
                ifname = "ethernet:2"
            if ifname == "network:3":
                ifname = "ethernet:3"
            if ifname == "network:4":
                ifname = "ethernet:4"
            if ifname == "network:5":
                ifname = "ethernet:5"
            if ifname == "network:6":
                ifname = "ethernet:6"
            if ifname == "network:7":
                ifname = "ethernet:7"
            if ifname in tagged_vlans:
                tagged_vlans[ifname] += [match.group("vlan_id")]
            else:
                tagged_vlans[ifname] = [match.group("vlan_id")]
        boards_status = self.get_boards_status_cli()
        self.logger.debug("Boards status: %s", boards_status)
        interfaces = {}
        uplink_found = False
        v = self.cli("show interface port detail")
        for p in v.split("----\nport\n----"):
            match = self.rx_ifname.search(p)
            if not match:
                continue
            ifname = match.group("ifname")
            hints = ["technology::dsl::adsl"]
            if ifname.startswith("ethernet"):
                uplink_found = True
                if ifname.startswith("ethernet:1/1/1:"):
                    port_id = "ethernet:" + ifname.split(":")[-1]
                else:
                    port_id = ifname
                hints = ["noc::topology::direction::nni", "technology::ethernet::1000base"]
            else:
                port_id = ifname.split(":", 1)[-1]
                slot_id = tuple(port_id.split("/")[:-1])
                if slot_id in boards_status and not boards_status[slot_id]:
                    self.logger.debug("Board is not enabled. Skipping...")
                    continue
            iftype = self.types.get(self.rx_type.search(p).group("type"))
            if not iftype or iftype == "other":
                continue
            interfaces[port_id] = {
                "name": port_id,
                "snmp_ifindex": self.rx_ifindex.search(p).group("ifindex"),
                "oper_status": self.rx_oper_status.search(p).group("oper_status") == "up",
                "admin_status": self.rx_admin_status.search(p).group("admin_status")
                in ["up", "admin-up"],
                "enabled_protocols": [],
                "subinterfaces": [],
                "type": iftype,
                "hints": hints,
            }
            if port_id in subifaces:
                interfaces[port_id]["subinterfaces"] += subifaces[port_id]
            if ifname.startswith("ethernet") and port_id not in subifaces:
                sub = {
                    "name": port_id,
                    "snmp_ifindex": self.rx_ifindex.search(p).group("ifindex"),
                    "oper_status": self.rx_oper_status.search(p).group("oper_status") == "up",
                    "admin_status": self.rx_admin_status.search(p).group("admin_status")
                    in ["up", "admin-up"],
                    "enabled_afi": ["BRIDGE"],
                }
                if tagged_vlans.get(port_id):
                    sub["tagged_vlans"] = tagged_vlans[port_id]
                interfaces[port_id]["subinterfaces"] += [sub]
            match = self.rx_mac.search(p)
            if match:
                interfaces[port_id]["mac"] = match.group("mac")
            match = self.rx_mtu.search(p)
            if match and int(match.group("mtu")) > 0:
                # interfaces["subinterfaces"][0]["mtu"] = match.group("mtu")
                pass

        if not uplink_found:
            # re-read the list of vlans
            # In this case interface name changed from `ethernet` to `network`
            tagged_vlans = {}
            v = self.cli("show vlan shub-port-vlan-map", cached=True)
            for match in self.rx_vlan_map.finditer(v):
                if int(match.group("vlan_id")) == 1:
                    continue
                ifname = match.group("ifname")
                if ifname in tagged_vlans:
                    tagged_vlans[ifname] += [match.group("vlan_id")]
                else:
                    tagged_vlans[ifname] = [match.group("vlan_id")]

            hints = ["noc::topology::direction::nni", "technology::ethernet::1000base"]
            v = self.cli("show interface shub port")
            for match in self.rx_uplink_port.finditer(v):
                port_id = "network:" + match.group("port")
                interfaces[port_id] = {
                    "name": port_id,
                    "oper_status": match.group("oper_status") == "up",
                    "admin_status": match.group("admin_status") == "up",
                    "subinterfaces": [],
                    "type": "physical",
                    "hints": hints,
                }
                sub = {
                    "name": port_id,
                    "oper_status": match.group("oper_status") == "up",
                    "admin_status": match.group("admin_status") == "up",
                    "enabled_afi": ["BRIDGE"],
                }
                if tagged_vlans.get(port_id):
                    sub["tagged_vlans"] = tagged_vlans[port_id]
                interfaces[port_id]["subinterfaces"] += [sub]

        v = self.cli("show ip shub vrf")
        for match in self.rx_ip.finditer(v):
            ip_address = match.group("ip")
            ip_subnet = match.group("mask")
            ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
            interfaces[match.group("iface")] = {
                "name": match.group("iface"),
                "admin_status": match.group("admin_status") == "up",
                "oper_status": match.group("oper_status") == "up",
                "type": "SVI",
                "enabled_protocols": [],
                "subinterfaces": [
                    {
                        "name": match.group("iface"),
                        "admin_status": match.group("admin_status") == "up",
                        "oper_status": match.group("oper_status") == "up",
                        "enabled_afi": ["IPv4"],
                        "ipv4_addresses": [ip_address],
                        "vlan_ids": [int(match.group("vlan_id"))],
                    }
                ],
            }

        try:
            v = self.cli("info configure system management flat")
            match = self.rx_mgmt_ip.search(v)
            if match:
                i = {
                    "name": "mgmt",
                    "type": "management",
                    "enabled_protocols": [],
                    "subinterfaces": [
                        {
                            "name": "mgmt",
                            "enabled_afi": ["IPv4"],
                            "ipv4_addresses": [match.group("ip")],
                        }
                    ],
                }
                match = self.rx_mgmt_vlan.search(v)
                if match:
                    i["subinterfaces"][0]["vlan_ids"] = [int(match.group("vlan_id"))]
            interfaces["mgmt"] = i
        except self.CLISyntaxError:
            v = self.cli("info configure system flat")
            mgmt = {"name": "mgmt", "type": "management", "subinterfaces": []}
            for match in self.rx_mgmt_ip2.finditer(v):
                sub = {
                    "name": "mgmt",
                    "enabled_afi": ["IPv4"],
                    "ipv4_addresses": [match.group("ip")],
                }
                if match.group("vlan_id"):
                    sub["vlan_ids"] = int(match.group("vlan_id"))
                    sub["name"] = "mgmt" + match.group("vlan_id")
                mgmt["subinterfaces"] += [sub]
            interfaces["mgmt"] = mgmt

        return [{"interfaces": list(interfaces.values())}]

    def get_boards_status(self):
        r = {}
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.637.61.1.23.3.1.8"):
            slot_id = oid.rsplit(".", 1)[-1]
            rack, shelf, slot = self.profile.get_slot(int(slot_id))
            slot = (rack, shelf, slot + 1)
            r[slot] = self.avail_status_map[v] in self.collected_slots_status
        return r

    def execute_snmp(self, **kwargs):
        ifaces = {}  # For interfaces
        subifaces = defaultdict(list)  # For subinterfaces like Fa 0/1.XXX
        ethernet = {}
        switchports = self.get_switchport()
        portchannels = self.get_portchannels()  # portchannel map
        boards_status = self.get_boards_status()
        ips = self.get_ip_ifaces()
        vci_ifindex_map = {}
        # iface -> vpi, vci, vciifindex
        for oid, vciifindex in self.snmp.getnext(
            "1.3.6.1.4.1.637.61.1.4.1.72.1.1",
            max_repetitions=self.get_max_repetitions(),
            max_retries=self.get_getnext_retires(),
        ):
            oid, ifindex, vpi, vci = oid.rsplit(".", 3)
            ifindex, vpi, vci = int(ifindex), int(vpi), int(vci)
            port_id = self.get_port_id(ifindex)
            name = "%d/%d/%d/%d:%d:%d" % tuple(list(port_id) + [vpi, vci])
            sub = {
                "name": name,
                "vci": vci,
                "vpi": vpi,
                "snmp_ifindex": vciifindex,
                "enabled_afi": ["ATM"],
            }
            vci_ifindex_map[ifindex] = vciifindex
            if vciifindex in switchports:
                sub.update(switchports[vciifindex])
                sub["enabled_afi"] += ["BRIDGE"]
            if vciifindex in ips:
                sub.update(ips[vciifindex])
                sub["enabled_afi"] += ["IPv4"]
            subifaces[port_id] += [sub]

        # Interface loop
        for oid, iftype in self.snmp.getnext(
            mib["IF-MIB::ifType"],
            max_repetitions=self.get_max_repetitions(),
            max_retries=self.get_getnext_retires(),
        ):
            if iftype not in self.PROCCESSED_TYPE:
                continue
            oid, ifindex = oid.rsplit(".", 1)
            ifindex = int(ifindex)
            port_id = self.get_port_id(ifindex)
            if port_id[:-1] in boards_status and not boards_status[port_id[:-1]]:
                self.logger.debug("Board is not enabled. Skipping...")
                continue
            ifname = "%d/%d/%d/%d" % port_id
            if "prefix" in self.PROCCESSED_TYPE[iftype]:
                ifname = "%s:%s" % (self.PROCCESSED_TYPE[iftype]["prefix"], ifname)
            if iftype in {6, 24}:
                # Ethernet ifaces
                hints = []
                if iftype == 6:
                    ifname = "ethernet:%s" % (port_id[-1] - 2)
                    hints = ["noc::topology::direction::nni"]
                ethernet[ifindex] = {
                    "name": ifname,
                    "snmp_ifindex": ifindex,
                    "enabled_protocols": [],
                    "subinterfaces": [],
                    "type": self.PROCCESSED_TYPE[iftype]["type"],
                    "hints": hints,
                }
            else:
                ifaces[ifindex] = {
                    "name": ifname,
                    "snmp_ifindex": ifindex,
                    "enabled_protocols": [],
                    "subinterfaces": [],
                    "type": self.PROCCESSED_TYPE[iftype]["type"],
                }

        # Fill interface info
        iter_tables = []
        iter_tables += [
            self.iter_iftable(
                "admin_status",
                self.SNMP_ADMIN_STATUS_TABLE,
                ifindexes=chain(ifaces, ethernet),
                clean=self.clean_status,
            )
        ]
        iter_tables += [
            self.iter_iftable(
                "oper_status",
                self.SNMP_OPER_STATUS_TABLE,
                ifindexes=chain(ifaces, ethernet),
                clean=self.clean_status,
            )
        ]
        iter_tables += [
            self.iter_iftable(
                "description",
                self.SNMP_IF_DESCR_TABLE,
                ifindexes=chain(ifaces, ethernet),
                clean=self.clean_ifdescription,
            )
        ]
        iter_tables += [
            self.iter_iftable(
                "mac", "IF-MIB::ifPhysAddress", ifindexes=ethernet, clean=self.clean_mac
            )
        ]
        iter_tables += [self.iter_iftable("mtu", "IF-MIB::ifMtu", ifindexes=ethernet)]
        # Collect and merge results
        data = self.merge_tables(*tuple(iter_tables))
        if not ifaces:
            # If empty result - raise error
            raise NotImplementedError
        # Format result to ifname -> iface
        interfaces = {}
        for ifindex, iface in ifaces.items():
            if ifindex in data:
                iface.update(data[ifindex])
            port_id = self.get_port_id(ifindex)
            if port_id in subifaces:
                iface["subinterfaces"] += subifaces[port_id]
            interfaces[iface["name"]] = iface
        for ifindex, iface in ethernet.items():
            # Ethernet ports
            if ifindex in data:
                iface.update(data[ifindex])
            port_id = self.get_port_id(ifindex)
            if port_id in subifaces:
                iface["subinterfaces"] += subifaces[port_id]
            if ifindex in ips:
                iface["subinterfaces"] += [
                    {
                        "name": iface["name"],
                        "enabled_afi": ["IPv4"],
                        "ipv4_addresses": [IPv4(*i) for i in ips[ifindex]],
                    }
                ]
            if ifindex in switchports:
                sub = {
                    "name": iface["name"],
                    "enabled_afi": ["BRIDGE"],
                }
                sub.update(switchports[ifindex])
                iface["subinterfaces"] += [sub]
            if ifindex in portchannels:
                iface["aggregated_interface"] = ifaces[portchannels[ifindex]]["name"]
                iface["enabled_protocols"] = ["LACP"]
            interfaces[iface["name"]] = iface
        return [{"interfaces": list(interfaces.values())}]

    def get_port_id(self, ifindex: int) -> Tuple[int, int, int, int]:
        # Convert ifindex to rack, shelf, slot, port
        slot_id = ifindex >> 16
        rack, shelf, slot = self.profile.get_slot(slot_id)
        port = ifindex & 0x00000FFF
        slot += 1
        return rack, shelf, slot, port + 1

    @staticmethod
    def clean_mac(mac: str):
        return mac or None
