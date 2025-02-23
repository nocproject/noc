# ---------------------------------------------------------------------
# Interface check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict

# Third-party modules
from pymongo import ReadPreference
from typing import Dict, List, Tuple, Set, Any, Optional

# NOC modules
from noc.core.text import ranges_to_list
from noc.services.discovery.jobs.base import PolicyDiscoveryCheck
from noc.core.vpn import get_vpn_id
from noc.core.service.rpc import RPCError
from noc.inv.models.forwardinginstance import ForwardingInstance
from noc.inv.models.interface import Interface
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.inv.models.subinterface import SubInterface
from noc.inv.models.technology import Technology
from noc.main.models.label import Label
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class InterfaceCheck(PolicyDiscoveryCheck):
    """
    Version discovery
    """

    name = "interface"
    required_script = "get_interfaces"

    AGG_QUERY = """Match("interfaces", if_name, "lag", "members", member)"""

    IF_QUERY = """(
        Match("interfaces", if_name) or
        Match("interfaces", if_name, "type", type) or
        Match("interfaces", if_name, "description", description) or
        Match("interfaces", if_name, "admin-status", admin_status)
    ) and Group("if_name")"""

    UNIT_QUERY = """(
        Match("virtual-router", vr, "forwarding-instance", instance, "interfaces", if_name, "unit", unit) or
        Match("virtual-router", vr, "forwarding-instance", instance, "interfaces", if_name, "unit", unit, "description", description) or
        Match("virtual-router", vr, "forwarding-instance", instance, "interfaces", if_name, "unit", unit, "inet", "address", ipv4_addresses) or
        Match("virtual-router", vr, "forwarding-instance", instance, "interfaces", if_name, "unit", unit, "inet6", "address", ipv6_addresses) or
        Match("virtual-router", vr, "forwarding-instance", instance, "interfaces", if_name, "unit", unit, "bridge", "switchport", "tagged", tagged) or
        Match("virtual-router", vr, "forwarding-instance", instance, "interfaces", if_name, "unit", unit, "bridge", "switchport", "untagged", untagged) or
        Match("virtual-router", vr, "forwarding-instance", instance, "interfaces", if_name, "unit", unit, "vlan_ids", vlan_ids)
    ) and Group("vr", "instance", "if_name", "unit", stack={"ipv4_addresses", "ipv6_addresses", "vlan_ids"})"""

    VRF_QUERY = """(Match("virtual-router", vr, "forwarding-instance", instance) or
        Match("virtual-router", vr, "forwarding-instance", instance, "type", type) or
        Match("virtual-router", vr, "forwarding-instance", instance, "vpn-id", vpn_id) or
        Match("virtual-router", vr, "forwarding-instance", instance, "route-distinguisher", rd) or
        Match("virtual-router", vr, "forwarding-instance", instance, "vrf-target", "export", rt_export) or
        Match("virtual-router", vr, "forwarding-instance", instance, "vrf-target", "import", rt_import)
    ) and Group("vr", "instance", stack={"rt_export", "rt_import"})"""

    PROTOCOLS_QUERY = """(Collapse("protocols", "lldp", "interface", if_name, "admin-status", join=",") or
        Match("protocols", "lldp", "interface", if_name, "admin-status", lldp_status) or
        Match("protocols", "spanning-tree", "interface", if_name, "admin-status", stp_status) or
        Match("protocols", "lacp", "interface", if_name, "mode", lacp_status)
    ) and Group("if_name")"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.get_interface_profile = partial(Label.get_instance_profile, InterfaceProfile)
        self.get_interface_profile = InterfaceProfile.get_profiles_matcher()
        self.get_subinterface_profile = InterfaceProfile.get_profiles_matcher(subinterface=True)
        self.confd_interface_profile_map = List[Tuple[str, InterfaceProfile]]
        self.interface_macs: Set[str] = set()
        self.seen_interfaces = []
        self.vrf_artefact: Dict[str, Dict[str, Any]] = {}  # name -> {name:, type:, rd:}
        self.prefix_artefact = {}
        self.interface_prefix_artefact: List[str] = []
        self.interface_assigned_vlans: Set[int] = set()  # @todo l2domain
        self.is_confdb_source = False  # Set True if Interface source is ConfDB
        self.allowed_labels = set(
            Label.objects.filter(allow_models=["inv.Interface"])
            .read_preference(ReadPreference.SECONDARY_PREFERRED)
            .values_list("name")
        )

    def handler(self):
        self.logger.info("Checking interfaces")
        result = self.get_data()
        if not result:
            self.logger.error("Failed to get interfaces")
            return
        if_map: Dict[str, Interface] = {}
        # Process forwarding instances
        for fi in result:
            vpn_id = fi.get("vpn_id")
            # Apply forwarding instance
            forwarding_instance = self.submit_forwarding_instance(
                name=fi["forwarding_instance"],
                fi_type=fi["type"],
                rd=fi.get("rd"),
                rt_export=fi.get("rt_export"),
                rt_import=fi.get("rt_import"),
                vr=fi.get("vr"),
                vpn_id=vpn_id,
            )
            # Move LAG members to the end
            # for effective caching
            ifaces = sorted(fi["interfaces"], key=self.in_lag)
            icache = {}
            for i in ifaces:
                # Get LAG
                agg = None
                if self.in_lag(i):
                    agg = icache.get(i["aggregated_interface"])
                    if not agg:
                        self.logger.error(
                            "Cannot find aggregated interface '%s'. Skipping %s",
                            i["aggregated_interface"],
                            i["name"],
                        )
                        continue
                # Submit discovered interface
                mac = i.get("mac")
                iface = self.submit_interface(
                    name=i["name"],
                    default_name=i.get("default_name"),
                    i_type=i["type"],
                    mac=mac,
                    description=i.get("description"),
                    aggregated_interface=agg,
                    enabled_protocols=i.get("enabled_protocols", []),
                    ifindex=i.get("snmp_ifindex"),
                    labels=i.get("hints", []),
                )
                icache[i["name"]] = iface
                # Submit subinterfaces
                for si in i["subinterfaces"]:
                    self.submit_subinterface(
                        forwarding_instance=forwarding_instance,
                        interface=iface,
                        name=si["name"],
                        description=si.get("description"),
                        mac=si.get("mac", i.get("mac")),
                        vlan_ids=si.get("vlan_ids", []),
                        enabled_afi=si.get("enabled_afi", []),
                        ipv4_addresses=si.get("ipv4_addresses", []),
                        ipv6_addresses=si.get("ipv6_addresses", []),
                        iso_addresses=si.get("iso_addresses", []),
                        vpi=si.get("vpi"),
                        vci=si.get("vci"),
                        enabled_protocols=si.get("enabled_protocols", []),
                        untagged_vlan=si.get("untagged_vlan"),
                        tagged_vlans=si.get("tagged_vlans", []),
                        # ip_unnumbered_subinterface
                        ifindex=si.get("snmp_ifindex"),
                    )
                    addresses = si.get("ipv4_addresses", []) + si.get("ipv6_addresses", [])
                    if addresses:
                        rd = forwarding_instance.rd if forwarding_instance else "0:0"
                        for a in addresses:
                            self.interface_prefix_artefact += [
                                {
                                    "vpn_id": vpn_id,
                                    "rd": rd,
                                    "address": a,
                                    "subinterface": si["name"],
                                    "description": si.get("description"),
                                    "mac": mac,
                                    "vlan_ids": si.get("vlan_ids", []),
                                }
                            ]
                # Delete hanging subinterfaces
                self.cleanup_subinterfaces(
                    forwarding_instance, iface, [si["name"] for si in i["subinterfaces"]]
                )
                # Update effective_labels
                el = Label.build_effective_labels(iface)
                self.logger.debug(
                    "[%s] Interface Calculated Effective labels: %s", iface.name, sorted(el)
                )
                if not iface.effective_labels or el != frozenset(iface.effective_labels):
                    self.logger.info(
                        "Interface '%s' has been changed: effective_labels = %s",
                        iface.name,
                        list(sorted(el)),
                    )
                    iface.save()
                changed = False
                el = Label.build_effective_labels(iface)
                if not iface.effective_labels or el != frozenset(iface.effective_labels):
                    iface.effective_labels = list(sorted(el))
                    changed = True
                # Perform interface classification
                self.interface_classification(iface)
                if changed:
                    iface.save()
                # Store for future collation
                if_map[iface.name] = iface
            # Delete hanging interfaces
            self.seen_interfaces += [i["name"] for i in fi["interfaces"]]
        # Interface Classification
        # self.interface_classification_bulk(if_map)
        # Delete hanging interfaces
        self.cleanup_interfaces(self.seen_interfaces)
        # Delete hanging forwarding instances
        self.cleanup_forwarding_instances([fi["forwarding_instance"] for fi in result])
        self.resolve_properties()
        self.update_caps(
            {"DB | Interfaces": Interface.objects.filter(managed_object=self.object.id).count()},
            source="interface",
        )
        #
        self.collate(if_map)
        # Set artifacts for future use
        self.set_artefact("interface_macs", self.interface_macs)
        self.set_artefact("interface_vpn", self.vrf_artefact)
        self.set_artefact("interface_prefix", self.interface_prefix_artefact)
        self.set_artefact("interface_assigned_vlans", self.interface_assigned_vlans)

    def submit_forwarding_instance(self, name, fi_type, rd, rt_export, rt_import, vr, vpn_id=None):
        if name == "default":
            return None
        rt_export = rt_export or []
        rt_import = rt_import or []
        forwarding_instance = ForwardingInstance.objects.filter(
            managed_object=self.object.id, name=name
        ).first()
        if forwarding_instance:
            changes = self.update_if_changed(
                forwarding_instance,
                {
                    "type": fi_type,
                    "name": name,
                    "vpn_id": vpn_id,
                    "rd": rd,
                    "rt_export": rt_export,
                    "rt_import": rt_import,
                },
            )
            self.log_changes(f"Forwarding instance '{name}' has been changed", changes)
        else:
            self.logger.info("Create forwarding instance '%s' (%s)", name, fi_type)
            forwarding_instance = ForwardingInstance(
                managed_object=self.object.id,
                name=name,
                type=fi_type,
                vpn_id=vpn_id,
                rd=rd,
                rt_export=rt_export,
                rt_import=rt_import,
                virtual_router=vr,
            )
            forwarding_instance.save()
        self.vrf_artefact[name] = {
            "name": name,
            "type": type,
            "rd": rd,
            "vpn_id": vpn_id,
            "rt_export": rt_export,
            "rt_import": rt_import,
        }
        return forwarding_instance

    def submit_interface(
        self,
        name: str,
        i_type: str,
        default_name: Optional[str] = None,
        mac: Optional[str] = None,
        description: Optional[str] = None,
        aggregated_interface=None,
        enabled_protocols: List[str] = None,
        ifindex: Optional[int] = None,
        labels: List[str] = None,
    ):
        enabled_protocols = enabled_protocols or []
        iface = self.get_interface_by_name(name)
        labels = labels or []
        extra_labels = []
        for ll in labels:
            if Interface.can_set_label(ll):
                if ll not in self.allowed_labels:
                    Label.ensure_label(ll, ["inv.Interface"])
                extra_labels.append(ll)
        if iface:
            ignore_empty = ["ifindex"]
            if self.is_confdb_source:
                ignore_empty = ["ifindex", "mac"]
            # Interface exists
            changes = self.update_if_changed(
                iface,
                {
                    "default_name": default_name,
                    "type": i_type,
                    "mac": mac,
                    "description": description,
                    "aggregated_interface": aggregated_interface,
                    "enabled_protocols": enabled_protocols,
                    "ifindex": ifindex,
                    "hints": labels or [],
                    "extra_labels": extra_labels,
                },
                ignore_empty=ignore_empty,
                update_effective_labels=False,
            )
            self.log_changes(f"Interface '{name}' has been changed", changes)
        else:
            # Create interface
            self.logger.info("Creating interface '%s'", name)
            iface = Interface(
                managed_object=self.object.id,
                name=name,
                type=i_type,
                mac=mac,
                description=description,
                aggregated_interface=aggregated_interface,
                enabled_protocols=enabled_protocols,
                ifindex=ifindex,
            )
            if labels:
                iface.labels = [ll for ll in labels if Interface.can_set_label(ll)]
                iface.extra_labels["sa"] = labels
            iface.save()
            self.set_interface(name, iface)
        if mac:
            self.interface_macs.add(mac)
        return iface

    def submit_subinterface(
        self,
        forwarding_instance: "ForwardingInstance",
        interface: "Interface",
        name: str,
        description: Optional[str] = None,
        mac: Optional[str] = None,
        vlan_ids: List[int] = None,
        enabled_afi: List[str] = None,
        ipv4_addresses: List[str] = None,
        ipv6_addresses: List[str] = None,
        iso_addresses: List[str] = None,
        vpi: Optional[int] = None,
        vci: Optional[int] = None,
        enabled_protocols: List[str] = None,
        untagged_vlan: Optional[int] = None,
        tagged_vlans: List[int] = None,
        ifindex: Optional[int] = None,
    ):
        mac = mac or interface.mac
        enabled_afi, enabled_protocols = enabled_afi or [], enabled_protocols or []
        ipv4_addresses, ipv6_addresses, iso_addresses = (
            ipv4_addresses or [],
            ipv6_addresses or [],
            iso_addresses or [],
        )
        tagged_vlans = tagged_vlans or []
        si = self.get_subinterface(interface, name)
        if si:
            ignore_empty = ["ifindex"]
            if self.is_confdb_source:
                ignore_empty = ["ifindex", "mac"]
            changes = self.update_if_changed(
                si,
                {
                    "forwarding_instance": forwarding_instance,
                    "description": description,
                    "mac": mac,
                    "vlan_ids": vlan_ids,
                    "enabled_afi": enabled_afi,
                    "ipv4_addresses": ipv4_addresses,
                    "ipv6_addresses": ipv6_addresses,
                    "iso_addresses": iso_addresses,
                    "vpi": vpi,
                    "vci": vci,
                    "enabled_protocols": enabled_protocols,
                    "untagged_vlan": untagged_vlan,
                    "tagged_vlans": tagged_vlans,
                    # ip_unnumbered_subinterface
                    "ifindex": ifindex,
                    # Update effective labels for exists subifaces
                },
                ignore_empty=ignore_empty,
                update_effective_labels=True,
            )
            self.log_changes(f"Subinterface '{name}' has been changed", changes)
        else:
            self.logger.info("Creating subinterface '%s'", name)
            si = SubInterface(
                forwarding_instance=forwarding_instance,
                interface=interface.id,
                managed_object=self.object.id,
                name=name,
                description=description,
                mac=mac,
                vlan_ids=vlan_ids,
                enabled_afi=enabled_afi,
                ipv4_addresses=ipv4_addresses,
                ipv6_addresses=ipv6_addresses,
                iso_addresses=iso_addresses,
                vpi=None,
                vci=None,
                enabled_protocols=enabled_protocols,
                untagged_vlan=untagged_vlan,
                tagged_vlans=tagged_vlans,
                ifindex=ifindex,
            )
            si.save()
        if mac:
            self.interface_macs.add(mac)
        if untagged_vlan:
            self.interface_assigned_vlans.add(untagged_vlan)
        if vlan_ids:
            self.interface_assigned_vlans.update(set(vlan_ids))
        self.subinterface_classification(si)
        return si

    def subinterface_classification(self, si: SubInterface):
        """Classification SubInterface"""
        if si.profile.subinterface_apply_policy == "I":
            return
        ctx = si.get_matcher_ctx()
        for p_id, match in self.get_subinterface_profile:
            if match(ctx):
                p = InterfaceProfile.get_by_id(p_id)
                break
        else:
            self.logger.debug("[%s] Nothing profile for match", si.name)
            p = InterfaceProfile.get_default_profile()
        if p and p.id != si.profile.id:
            si.profile = p
            si.save()

    def cleanup_forwarding_instances(self, fi: List[str]):
        """
        Delete hanging forwarding instances
        :param fi: generator yielding instance names
        :return:
        """
        db_fi: Set[str] = set(
            i["name"]
            for i in ForwardingInstance.objects.filter(managed_object=self.object.id).only("name")
        )
        for i in db_fi - set(fi):
            self.logger.info("Removing forwarding instance %s", i)
            for dfi in ForwardingInstance.objects.filter(managed_object=self.object.id, name=i):
                dfi.delete()

    def cleanup_interfaces(self, interfaces: List[str]):
        """
        Delete hanging interfaces
        Attrs:
            interfaces: generator yielding interfaces names
        """
        db_iface: Set[str] = set(
            i["name"] for i in Interface.objects.filter(managed_object=self.object.id).only("name")
        )
        for i in db_iface - set(interfaces):
            self.logger.info("Removing interface %s", i)
            di = Interface.objects.filter(managed_object=self.object.id, name=i).first()
            if di:
                di.delete()

    def cleanup_subinterfaces(
        self,
        forwarding_instance: "ForwardingInstance",
        interface: "Interface",
        subinterfaces: List[str],
    ):
        """
        Delete hanging subinterfaces
        """
        if forwarding_instance:
            fi = forwarding_instance.id
        else:
            fi = None
        qs = SubInterface.objects.filter(
            managed_object=self.object.id, interface=interface.id, forwarding_instance=fi
        )
        db_siface: Set[str] = set(i["name"] for i in qs.only("name"))
        for i in db_siface - set(subinterfaces):
            self.logger.info("Removing subinterface %s", i)
            dsi = SubInterface.objects.filter(
                managed_object=self.object.id, interface=interface.id, name=i
            ).first()
            if dsi:
                dsi.delete()

    def interface_classification(self, iface: Interface):
        """
        Perform interface classification
        For Aggregate members profile inheritance from aggregate interface, if not has profile Member label
        Attrs:
            iface: Interface instance
        """
        if iface.profile_locked:
            self.logger.info(
                "[%s] Interface %s profile set by User. That block for classification",
                iface.name,
                iface.profile.name,
            )
            return
        elif iface.aggregated_interface and iface.aggregated_interface.profile != iface.profile:
            iface.profile = iface.aggregated_interface.profile
            self.logger.info(
                "[%s] Interface has been classified from members '%s'",
                iface.name,
                iface.aggregated_interface.name,
            )
            iface.save()
            return
        elif iface.aggregated_interface:
            return
        ctx = iface.get_matcher_ctx()
        for p_id, match in self.get_interface_profile:
            if match(ctx):
                break
        else:
            self.logger.debug("[%s] Nothing profile for match", iface.name)
            return
        if p_id and p_id != iface.profile.id:
            # Change profile
            profile = InterfaceProfile.get_by_id(p_id)
            if not profile:
                self.logger.error(
                    "[%s] Invalid interface profile '%s'. Skipping",
                    iface.name,
                    p_id,
                )
                return
            elif profile != iface.profile:
                self.logger.info(
                    "[%s] Interface has been classified as '%s'", iface.name, profile.name
                )
                iface.profile = profile
                iface.save()

    def resolve_properties(self):
        """Try to resolve missed ifindexes and mac"""
        resolve_ifindex, resolve_mac = True, False
        iface_discovery_policy = self.object.get_interface_discovery_policy()
        if iface_discovery_policy == "c":
            self.logger.info("Cannot resolve ifindexes due to policy")
            return
        elif self.is_confdb_source:
            self.logger.info("Resolve ifindexes and macs by script")
            resolve_mac = True
        # Missed properties
        missed_properties = [
            n[1]
            for n in self.if_name_cache
            if (
                n in self.if_name_cache
                and self.if_name_cache[n]
                and (
                    (resolve_ifindex and self.if_name_cache[n].ifindex is None)
                    or (resolve_mac and self.if_name_cache[n].mac is None)
                )
                and self.if_name_cache[n].type in ("physical", "aggregated")
            )
        ]
        if not missed_properties:
            return
        self.logger.info("Missed properties for: %s", ", ".join(missed_properties))
        if "get_interface_properties" not in self.object.scripts:
            self.logger.info(
                "Profile %s not supported 'get_interface_properties' script",
                self.object.profile.name,
            )
            return
        try:
            r = self.object.scripts.get_interface_properties(
                enable_ifindex=resolve_ifindex, enable_interface_mac=resolve_mac
            )
        except RPCError:
            r = None
        if not r:
            return
        updates = defaultdict(dict)
        for i in r:
            if i["interface"] not in missed_properties:
                continue
            if resolve_ifindex:
                updates[i["interface"]]["ifindex"] = i["ifindex"]
            if resolve_mac:
                updates[i["interface"]]["mac"] = i["mac"]
                self.interface_macs.add(i["mac"])
        if not updates:
            return
        for n, i in updates.items():
            iface = self.get_interface_by_name(n)
            if iface:
                if "ifindex" in i:
                    self.logger.info("Set ifindex for %s: %s", n, i["ifindex"])
                    iface.ifindex = i["ifindex"]
                if "mac" in i:
                    self.logger.info("Set mac for %s: %s", n, i["mac"])
                    iface.mac = i["mac"]
                iface.save()  # Signals will be sent

    @staticmethod
    def in_lag(x) -> bool:
        return "aggregated_interface" in x and bool(x["aggregated_interface"])

    def get_policy(self):
        return self.object.get_interface_discovery_policy()

    def get_data_from_script(self):
        return self.object.scripts.get_interfaces()

    def get_data_from_confdb(self) -> List[Dict[str, Any]]:
        self.is_confdb_source = True
        # Get interfaces and parse result
        interfaces = {d["if_name"]: d for d in self.confdb.query(self.IF_QUERY)}
        vrfs = {(d["vr"], d["instance"]): d for d in self.confdb.query(self.VRF_QUERY)}
        iface_proto = {d["if_name"]: d for d in self.confdb.query(self.PROTOCOLS_QUERY)}
        aggregated = {d["member"]: d["if_name"] for d in self.confdb.query(self.AGG_QUERY)}
        instances = defaultdict(dict)
        for d in self.confdb.query(self.UNIT_QUERY):
            r = instances[d["vr"], d["instance"]]
            if not r:
                r["virtual_router"] = d["vr"]
                r["forwarding_instance"] = d["instance"]
                if vrfs and (d["vr"], d["instance"]) in vrfs:
                    try:
                        vrf = vrfs[d["vr"], d["instance"]]
                        r["type"] = vrf["type"]
                        if vrf.get("rd"):
                            r["rd"] = vrf["rd"]
                        r["rt_export"] = vrf.get("rt_export", [])
                        if vrf.get("rt_import"):
                            r["rt_import"] = vrf["rt_import"]
                        if "vpn_id" in vrf:
                            r["vpn_id"] = vrf["vpn_id"]
                        else:
                            r["vpn_id"] = get_vpn_id(
                                {
                                    "name": vrf["instance"],
                                    "rd": vrf.get("rd"),
                                    "rt_export": vrf.get("rt_export", []),
                                    "type": (
                                        vrf["type"].upper()
                                        if vrf["type"] in ["vrf", "vpls", "vll"]
                                        else vrf["type"]
                                    ),
                                }
                            )
                    except ValueError:
                        pass
            if "interfaces" not in r:
                r["interfaces"] = {}
            if_name = d["if_name"]
            p_iface = interfaces.get(if_name)
            iface: Dict[str, Any] = r["interfaces"].get(if_name)
            if iface is None:
                iface = {
                    "name": if_name,
                    "type": p_iface.get("type", "unknown") if p_iface else "unknown",
                    "admin_status": False,
                    "enabled_protocols": [],
                    "subinterfaces": {},
                }
                r["interfaces"][if_name] = iface
                if p_iface:
                    if "description" in p_iface:
                        iface["description"] = p_iface["description"]
                    if "admin_status" in p_iface:
                        iface["admin_status"] = p_iface["admin_status"]
                    if if_name in iface_proto:
                        if iface_proto[if_name].get("stp_status") == "on":
                            iface["enabled_protocols"] += ["STP"]
                        if iface_proto[if_name].get("lldp_status"):
                            iface["enabled_protocols"] += ["LLDP"]
                        if iface_proto[if_name].get("lacp_status"):
                            iface["enabled_protocols"] += ["LACP"]
                    if if_name in aggregated:
                        iface["aggregated_interface"] = aggregated[if_name]
            unit: Dict[str, Any] = iface["subinterfaces"].get(d["unit"])
            if unit is None:
                unit = {"name": d["unit"], "enabled_afi": []}
                iface["subinterfaces"][d["unit"]] = unit
            unit = iface["subinterfaces"][d["unit"]]
            description = d.get("description")
            if description:
                unit["description"] = description
            elif p_iface and p_iface.get("description"):
                unit["description"] = p_iface["description"]
            if "ipv4_addresses" in d:
                unit["enabled_afi"] += ["IPv4"]
                unit["ipv4_addresses"] = d["ipv4_addresses"]
            if "ipv6_addresses" in d:
                unit["enabled_afi"] += ["IPv6"]
                unit["ipv6_addresses"] = d["ipv4_addresses"]
            if "tagged" in d or "untagged" in d:
                unit["enabled_afi"] += ["BRIDGE"]
            if "untagged" in d:
                unit["untagged_vlan"] = int(d["untagged"])
            if "tagged" in d:
                unit["tagged_vlans"] = ranges_to_list(d["tagged"])
            if "vlan_ids" in d:
                unit["vlan_ids"] = d["vlan_ids"]
        # Flatten units
        r = list(instances.values())
        for fi in r:
            # Flatten interfaces
            fi["interfaces"] = list(fi["interfaces"].values())
            # Flatten units
            for i in fi["interfaces"]:
                i["subinterfaces"] = list(i["subinterfaces"].values())
        return IGetInterfaces().clean_result(r)

    def collate(self, if_map: Dict[str, Interface]) -> None:
        """
        Collation is the process of binding between physical and logical inventory.
        I.e. assigning interface names to inventory slots.

        :param if_map:
        :returns:
        """

        def path_to_str(p):
            return " > ".join(x.connection.name for x in p)

        if not self.object.object_profile.enable_box_discovery_asset:
            self.logger.info("asset discovery is disabled. Skipping collation process")
            return
        if not if_map:
            self.logger.info("No interfaces found. Skipping collation process")
            return
        # Build collators chain
        chain = list(self.object.profile.get_profile().iter_collators(self.object))
        if not chain:
            self.logger.info("Collator chain is empty. Skipping collation process.")
            return
        # Perform collation
        self.logger.info("Starting interface collation")
        mappings = defaultdict(list)  # object -> [(connection_name, if_name), ...]
        seen_objects = set()  # {object}
        obj_combined = {}  # object -> connection name -> parent name
        obj_ifnames = {}  # object -> connection name -> interface name
        ethernet_t = Technology.get_by_name("Ethernet")
        xcvr_t = Technology.get_by_name("Transceiver")
        for port in self.object.iter_technology([ethernet_t, xcvr_t]):
            if_name = None
            obj = port.path[-1].object
            if obj not in seen_objects:
                obj_combined[obj] = {c.name: c.combo for c in obj.model.connections if c.combo}
                obj_ifnames[obj] = {}
                seen_objects.add(obj)
            cn = port.path[-1].connection.name
            parent = obj_combined[obj].get(cn)
            if parent:
                # Combined port, try to resolve against parent
                if_name = obj_ifnames[obj].get(parent)
                if if_name:
                    # Parent is already bound
                    obj_ifnames[obj][cn] = if_name
                    mappings[obj] += [(port.path, if_name)]
                    self.logger.info(
                        "%s mapped to interface %s via parent %s",
                        path_to_str(port.path),
                        if_name,
                        parent,
                    )
            if not if_name:
                for collator in chain:
                    if_name = collator.collate(port, if_map)
                    if if_name:
                        obj_ifnames[obj][cn] = if_name
                        mappings[obj] += [(port.path, if_name)]
                        self.logger.info(
                            "%s mapped to interface %s", path_to_str(port.path), if_name
                        )
                        break
            if not if_name:
                self.logger.info("Unable to map %s to interface", path_to_str(port.path))
        # Bulk update data
        for obj in seen_objects:
            old_if_map = {c.name: c.interface_name for c in obj.connections if c.interface_name}
            changed = False
            for path, if_name in mappings[obj]:
                connection_name = path[-1].connection.name
                if connection_name not in old_if_map:
                    # New
                    self.logger.info("Map %s to %s", path_to_str(path), if_name)
                    obj.set_connection_interface(connection_name, if_name)
                    changed = True
                    continue
                if old_if_map[connection_name] != if_name:
                    # Changed
                    self.logger.info(
                        "Map %s to %s (was %s)",
                        path_to_str(path),
                        if_name,
                        old_if_map[connection_name],
                    )
                    obj.set_connection_interface(connection_name, if_name)
                    changed = True
                # Mark as processed
                del old_if_map[connection_name]
            if old_if_map:
                # Process removed
                for connection_name in old_if_map:
                    self.logger.info(
                        "Unmap %s from %s", connection_name, old_if_map[connection_name]
                    )
                    obj.reset_connection_interface(connection_name)
                changed = True
            # Apply changes
            if changed:
                obj.save()
