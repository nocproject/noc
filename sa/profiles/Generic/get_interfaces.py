# ---------------------------------------------------------------------
# Generic.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from typing import (
    Dict,
    Optional,
    Union,
    Iterable,
    Tuple,
    Callable,
    List,
    Any,
    Iterator,
    DefaultDict,
)
from collections import defaultdict
from itertools import chain

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.mib import mib
from noc.core.ip import IPv4
from noc.core.snmp.render import render_bin
from noc.core.comp import smart_text
from noc.core.mac import MAC
from noc.core.validators import is_mac, is_vlan


class Script(BaseScript):
    name = "Generic.get_interfaces"
    interface = IGetInterfaces
    MAX_REPETITIONS = 30
    MAX_GETNEXT_RETIRES = 1
    MAX_TIMEOUT = 20
    INVALID_MTU = 2147483647
    CHUNK_SIZE = 20

    # Replace on get_interface_properties
    # SNMP_NAME_TABLE = "IF-MIB::ifDescr"
    # SNMP_MAC_TABLE = "IF-MIB::ifPhysAddress"
    SNMP_ADMIN_STATUS_TABLE = "IF-MIB::ifAdminStatus"
    SNMP_OPER_STATUS_TABLE = "IF-MIB::ifOperStatus"
    SNMP_IF_DESCR_TABLE = "IF-MIB::ifAlias"
    SNMP_MAC_TABLE = "IF-MIB::ifPhysAddress"

    IGNORED_MACS = {
        "00:00:00:00:00:00",  # Empty MAC
        "00:01:02:03:04:00",  # Very Smart programmer
        "00:01:02:03:04:05",  # Very Smart+ programmer
        "FF:FF:FF:FF:FF:FF",  # Broadcast
    }

    rx_vlan_interface = re.compile(r"^vlan\w*?\s*?(?P<vlan_num>\d+)$", re.IGNORECASE)

    def get_bridge_ifindex_mappings(self) -> Dict[int, int]:
        """
        Getting mappings for bridge port number -> ifindex
        :return:
        """
        pid_ifindex_mappings = {}
        for oid, v in self.snmp.getnext(
            mib["BRIDGE-MIB::dot1dBasePortIfIndex"],
            max_repetitions=self.get_max_repetitions(),
            max_retries=self.get_getnext_retires(),
            timeout=self.get_snmp_timeout(),
        ):
            pid_ifindex_mappings[int(oid.split(".")[-1])] = v
        return pid_ifindex_mappings

    def get_port_vlan_oids(self) -> Tuple[str, str]:
        """Return oid for collection port <-> Vlan map"""
        if self.has_capability("SNMP | MIB | IEEE8021-Q-BRIDGE-MIB"):
            self.logger.debug("Use IEEE8021-Q-BRIDGE-MIB for collected switchport")
            return (
                mib["IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgePvid"],
                mib["IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVlanCurrentEgressPorts"],
            )
        return mib["Q-BRIDGE-MIB::dot1qPvid"], mib["Q-BRIDGE-MIB::dot1qVlanCurrentEgressPorts"]

    def get_switchport(self) -> DefaultDict[int, Dict[str, Union[int, list, None]]]:
        # noc::interface::bridge_mode:: access/trunk/hybrid
        result = defaultdict(lambda: {"tagged_vlans": [], "untagged_vlan": None})
        pid_ifindex_mappings = self.get_bridge_ifindex_mappings()
        self.logger.debug("PID <-> ifindex mappings: %s", pid_ifindex_mappings)
        pvid_oid, tagged_oid = self.get_port_vlan_oids()
        for oid, pvid in self.snmp.getnext(
            pvid_oid,
            max_repetitions=self.get_max_repetitions(),
            max_retries=self.get_getnext_retires(),
            timeout=self.get_snmp_timeout(),
        ):
            if not pvid:
                # if pvid is 0
                continue
            elif not is_vlan(pvid):
                # on Alcatel DSLAM it 16777217
                self.logger.warning(
                    "Bad value for untagged vlan.Skipping.. oid %s: vlan %s", oid, pvid
                )
                continue
            o = int(oid.split(".")[-1])
            if o in pid_ifindex_mappings:
                o = pid_ifindex_mappings[o]
            else:
                self.logger.warning("PortID %s not in ifindex mapping. Use as is", o)
            result[o]["untagged_vlan"] = pvid
        for oid, ports_mask in self.snmp.getnext(
            tagged_oid,
            max_repetitions=self.get_max_repetitions(),
            max_retries=self.get_getnext_retires(),
            display_hints={tagged_oid: render_bin},
            timeout=self.get_snmp_timeout(),
        ):
            vlan_num = int(oid.split(".")[-1])
            # Getting port as mask,  convert to vlan: Iface list
            for port, is_egress in enumerate(
                chain.from_iterable("{0:08b}".format(mask) for mask in ports_mask), start=1
            ):
                if is_egress == "0":
                    continue
                elif port not in pid_ifindex_mappings:
                    self.logger.error("Port %s not in PID mappings", port)
                    continue
                elif vlan_num == result[pid_ifindex_mappings[port]]["untagged_vlan"]:
                    continue
                result[pid_ifindex_mappings[port]]["tagged_vlans"] += [vlan_num]
        return result

    def get_portchannels(self) -> Dict[int, int]:
        r = {}
        for ifindex, sel_pc, att_pc in self.snmp.get_tables(
            [
                mib["IEEE8023-LAG-MIB::dot3adAggPortSelectedAggID"],
                mib["IEEE8023-LAG-MIB::dot3adAggPortAttachedAggID"],
            ]
        ):
            if att_pc and att_pc != int(ifindex):
                if sel_pc > 0:
                    r[int(ifindex)] = int(att_pc)
        return r

    def get_enabled_proto(self):
        return {}

    def get_ip_ifaces(self) -> Dict[int, List[IPv4]]:
        """Getting IP Address -> iface by RFC1213-MIB"""
        r = defaultdict(list)
        ip_mask = {}
        for oid, mask in self.snmp.getnext(
            mib["RFC1213-MIB::ipAdEntNetMask"],
            max_repetitions=self.get_max_repetitions(),
            max_retries=self.get_getnext_retires(),
        ):
            address = oid.split(mib["RFC1213-MIB::ipAdEntNetMask"])[-1].strip(".")
            ip_mask[address] = [IPv4(address, mask)]
        for oid, ifindex in self.snmp.getnext(
            mib["RFC1213-MIB::ipAdEntIfIndex"],
            max_repetitions=self.get_max_repetitions(),
            max_retries=self.get_getnext_retires(),
        ):
            address = oid.split(mib["RFC1213-MIB::ipAdEntIfIndex"])[-1].strip(".")
            r[ifindex] += ip_mask[address]
        return r

    def get_ip_ifaces_ip_mib(self) -> Dict[int, List[IPv4]]:
        """Getting IP Address -> Iface by IP-MIB"""
        r = defaultdict(list)
        ip_mask = {}
        for oid, mask in self.snmp.getnext(
            mib["IP-MIB::ipAddressPrefix"],
            max_repetitions=self.get_max_repetitions(),
            max_retries=self.get_getnext_retires(),
        ):
            _, index = oid.split(mib["IP-MIB::ipAddressPrefix"])
            _, a_type, address = index.strip(".").split(".", 2)
            # address = oid.split(mib["IP-MIB::ipAddressPrefix"])[-1].strip(".")
            ip_mask[address] = [IPv4(f"{address}/{mask.rsplit('.', 1)[-1]}")]
        for oid, ifindex in self.snmp.getnext(
            mib["IP-MIB::ipAddressIfIndex"],
            max_repetitions=self.get_max_repetitions(),
            max_retries=self.get_getnext_retires(),
        ):
            _, index = oid.split(mib["IP-MIB::ipAddressIfIndex"])
            _, a_type, address = index.strip(".").split(".", 2)
            # address = oid.split(mib["IP-MIB::ipAddressIfIndex"])[-1].strip(".")
            r[ifindex] += ip_mask[address]
        return r

    def get_mpls_vpn_mappings(self) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, str]]:
        # Process VRFs
        vrfs = {"default": {"forwarding_instance": "default", "type": "table", "interfaces": []}}
        imap = {}  # interface -> VRF
        try:
            r = self.scripts.get_mpls_vpn()
        except self.CLISyntaxError:
            r = []
        for v in r:
            vrfs[v["name"]] = {
                "forwarding_instance": v["name"],
                "type": v["type"],
                "vpn_id": v.get("vpn_id"),
                "interfaces": [],
            }
            rd = v.get("rd")
            if rd:
                vrfs[v["name"]]["rd"] = rd
            for i in v["interfaces"]:
                imap[i] = v["name"]
        return vrfs, imap

    def filter_interface(self, ifindex: int, name: str, oper_status: bool) -> bool:
        """
        Filter interface
        :param ifindex:
        :param name:
        :param oper_status:
        :return:
        """
        return True

    def is_subinterface(self, iface):
        if "." in iface:
            return True

    def execute_snmp(self, **kwargs):
        ifaces = {}  # For interfaces
        subifaces = {}  # For subinterfaces like Fa 0/1.XXX
        switchports = self.get_switchport()
        portchannels = self.get_portchannels()  # portchannel map
        if self.has_capability("SNMP | OID | RFC1213-MIB::ipAddrTable"):
            ips = self.get_ip_ifaces()
        else:
            self.logger.debug("Use IP-MIB for getting iface -> IP Address bind")
            ips = self.get_ip_ifaces_ip_mib()
        if not ips:
            self.logger.info("Not found iface -> IP Address bind")
        # Getting initial iface info, filter result if needed
        for iface in self.scripts.get_interface_properties(
            enable_ifindex=True, enable_oper_status=True
        ):
            if not self.filter_interface(
                iface["ifindex"], iface["interface"], iface.get("oper_status")
            ):
                continue
            if self.is_subinterface(iface["interface"]):
                subifaces[iface["ifindex"]] = {
                    "name": iface["interface"],
                    "snmp_ifindex": iface["ifindex"],
                    "oper_status": iface.get("oper_status", True),
                }
                # if "mac" in iface:
                #     subifaces[iface["ifindex"]]["mac"] = iface["mac"]
            else:
                ifaces[iface["ifindex"]] = {
                    "name": iface["interface"],
                    "snmp_ifindex": iface["ifindex"],
                    "oper_status": iface.get("oper_status", True),
                    "enabled_protocols": [],
                    "subinterfaces": [],
                }
                # if "mac" in iface:
                #     ifaces[iface["ifindex"]]["mac"] = iface["mac"]
        # Fill interface info
        iter_tables = []
        iter_tables += [
            self.iter_iftable(
                "admin_status",
                self.SNMP_ADMIN_STATUS_TABLE,
                ifindexes=ifaces,
                clean=self.clean_status,
            )
        ]
        iter_tables += [
            self.iter_iftable("mac", self.SNMP_MAC_TABLE, ifindexes=ifaces, clean=self.clean_mac)
        ]
        iter_tables += [
            self.iter_iftable(
                "description",
                self.SNMP_IF_DESCR_TABLE,
                ifindexes=chain(ifaces, subifaces),
                clean=self.clean_ifdescription,
            )
        ]
        iter_tables += [
            self.iter_iftable(
                "mtu", "IF-MIB::ifMtu", ifindexes=chain(ifaces, subifaces), clean=self.clean_mtu
            )
        ]
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
            iface["type"] = self.clean_iftype(iface["name"], ifindex)
            if not iface["type"]:
                self.logger.error("Unknown type for interface %s", iface["name"])
                continue
            if ifindex in ips:
                iface["subinterfaces"] += [
                    {
                        "name": iface["name"],
                        "enabled_afi": ["IPv4"],
                        "ipv4_addresses": [str(i) for i in ips[ifindex]],
                    }
                ]
                vlan_iface_match = self.rx_vlan_interface.match(iface["name"])
                if vlan_iface_match and is_vlan(vlan_iface_match.group("vlan_num")):
                    iface["subinterfaces"][-1]["vlan_ids"] = [
                        int(vlan_iface_match.group("vlan_num"))
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
        # Proccessed subinterfaces
        for ifindex, sub in subifaces.items():
            ifname, num = sub["name"].split(".", 1)
            if ifname not in interfaces:
                self.logger.info("Sub %s for ignored iface %s", sub["name"], ifname)
                continue
            if ifindex in data:
                sub.update(data[ifindex])
            if ifindex in ips:
                sub["enabled_afi"] = ["IPv4"]
                sub["ipv4_addresses"] = [str(i) for i in ips[ifindex]]
            if ifindex in portchannels:
                # For Juniper Aggregated Interface use unit - '.0' ifindex
                interfaces[ifname]["aggregated_interface"] = ifaces[portchannels[ifindex]]["name"]
                interfaces[ifname]["enabled_protocols"] = ["LACP"]
            if num.isdigit():
                vlan_ids = int(sub["name"].rsplit(".", 1)[-1])
                if is_vlan(vlan_ids):
                    sub["vlan_ids"] = vlan_ids
            interfaces[ifname]["subinterfaces"] += [sub]
        # VRF and forwarding_instance proccessed
        vrfs, vrf_if_map = self.get_mpls_vpn_mappings()
        for i in interfaces.keys():
            iface_vrf = "default"
            subs = interfaces[i]["subinterfaces"]
            interfaces[i]["subinterfaces"] = []
            if i in vrf_if_map:
                iface_vrf = vrf_if_map[i]
                vrfs[vrf_if_map[i]]["interfaces"] += [interfaces[i]]
            else:
                vrfs["default"]["interfaces"] += [interfaces[i]]
            for s in subs:
                if s["name"] in vrf_if_map and vrf_if_map[s["name"]] != iface_vrf:
                    vrfs[vrf_if_map[s["name"]]]["interfaces"] += [
                        {
                            "name": s["name"],
                            "type": "other",
                            "enabled_protocols": [],
                            "subinterfaces": [s],
                        }
                    ]
                else:
                    interfaces[i]["subinterfaces"] += [s]
        return list(vrfs.values())

    def merge_tables(
        self, *args: Optional[Iterable]
    ) -> Dict[int, Dict[str, Union[int, bool, str]]]:
        """
        Merge iterables into single table

        :param args:
        :return:
        """
        r = {}
        for iter_table in args:
            for key, ifindex, value in iter_table:
                if ifindex not in r:
                    r[ifindex] = {"snmp_ifindex": ifindex}
                r[ifindex][key] = value
        return r

    @staticmethod
    def clean_default(v):
        return v

    @staticmethod
    def clean_status(v):
        return v == 1

    def clean_ifname(self, v):
        return self.profile.convert_interface_name(v)

    # if ascii or rus text in description
    def clean_ifdescription(self, desc):
        if desc:
            return smart_text(desc, errors="replace")
        return desc

    def clean_iftype(self, ifname: str, ifindex: Optional[int] = None) -> str:
        return self.profile.get_interface_type(ifname)

    def clean_mac(self, mac: str):
        if is_mac(mac) and not self.is_ignored_mac(MAC(mac)):
            return mac
        return None

    def clean_mtu(self, mtu: int):
        if not mtu:
            raise ValueError
        mtu = int(mtu)
        if mtu == self.INVALID_MTU:
            raise ValueError
        return mtu

    def iter_iftable(
        self, key: str, oid: str, ifindexes: Optional[Iterator[int]] = None, clean: Callable = None
    ) -> Iterable[Tuple[str, Union[str, int]]]:
        """
        Collect part of IF-MIB table.

        :param key:
        :param oid: Base oid, either in numeric or symbolic form
        :param ifindexes: Collect information for single interface only, if set
        :param clean: Cleaning function
        :return:
        """
        clean = clean or self.clean_default
        # Partial
        if ifindexes:
            for r_oid, v in self.snmp.get_chunked(
                [mib[oid, i] for i in ifindexes],
                chunk_size=self.get_chunk_size(),
                timeout_limits=self.get_snmp_timeout(),
            ).items():
                try:
                    yield key, int(r_oid.rsplit(".", 1)[1]), clean(v)
                except ValueError:
                    pass
        else:
            # All interfaces
            if "::" in oid:
                oid = mib[oid]
            for r_oid, v in self.snmp.getnext(
                oid,
                max_repetitions=self.get_max_repetitions(),
                max_retries=self.get_getnext_retires(),
            ):
                try:
                    yield key, int(r_oid.rsplit(".", 1)[1]), clean(v)
                except ValueError:
                    pass

    def get_max_repetitions(self):
        return self.MAX_REPETITIONS

    def get_getnext_retires(self):
        return self.MAX_GETNEXT_RETIRES

    def get_snmp_timeout(self):
        return self.MAX_TIMEOUT

    def get_chunk_size(self):
        return self.CHUNK_SIZE

    def get_interface_ifindex(self, name: str) -> int:
        """
        Get ifindex for given interface
        :param name:
        :return:
        """
        for r_oid, v in self.snmp.getnext(
            mib[self.SNMP_NAME_TABLE],
            max_repetitions=self.get_max_repetitions(),
            max_retries=self.get_getnext_retires(),
        ):
            if self.profile.convert_interface_name(v) == name:
                return int(r_oid.rsplit(".", 1)[1])
        raise KeyError

    def iter_interface_ifindex(self, name, ifindex):
        yield "name", ifindex, self.profile.convert_interface_name(name)

    def is_ignored_mac(self, mac: MAC) -> bool:
        """
        Check if MAC address should be ignored
        :param mac: Normalized MAC address
        :return: True if MAC should be ignored
        """
        return mac in self.IGNORED_MACS or mac.is_multicast
