# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ZTE.ZXR10.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
import copy
from collections import defaultdict
# NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces


class Script(NOCScript):
    """
    ZTE.ZXR10.get_interfaces
    """
    name = "ZTE.ZXR10.get_interfaces"
    implements = [IGetInterfaces]

    rx_int = re.compile(r"^(?P<name>.+?)\sis\s(?P<status>(?:administratively )?\S+),.+\sline.+$")
    rx_descr = re.compile(r"^\s+Description\sis\s+(?P<descr>.+?)\s*$")
    rx_inet = re.compile(r"^\s+Internet\saddress\sis\s+(?P<inet>\S+)")
    rx_mac = re.compile(r"^\s+MAC\saddress\sis\s+(?P<mac>\S+)")
    rx_mtu = re.compile(r"^\s+MTU\s(?P<mtu>\d+)\sbytes\s+BW")
    rx_lag = re.compile(r"^Smartgroup\:(?P<lag>\d+)")
    rx_lag_member = re.compile(r"^(?P<lag_member>x?gei_\S+)")

    def execute(self):
        ifaces = {}
        last_if = None
        if_list = []
        subs = defaultdict(list)
        vlans_raw = self.cli("show vlan").splitlines()
        vlan_set = self.get_vlan(vlans_raw)
        for l in self.cli("show interface").splitlines():
            # New interface
            match = self.rx_int.search(l)
            if match:
                last_if = match.group("name")
                if_list += [last_if]  # preserve order
                ifaces[last_if] = {
                    "name": last_if,
                    "ipv4_addresses": [],
                    "type": self.type_by_name(last_if),
                    "admin_status": "",
                    "oper_status": "",
                    "enabled_protocols": [],
                    "subinterfaces": []
                }

            # interface admin and oper status
                if match.group("status") == "administratively down":
                    ifaces[last_if]["admin_status"] = False
                    ifaces[last_if]["oper_status"] = False
                else:
                    ifaces[last_if]["admin_status"] = True
                    if match.group("status") == "down":
                        ifaces[last_if]["oper_status"] = False
                    else:
                        ifaces[last_if]["oper_status"] = True
                continue
            # Description
            match = self.rx_descr.search(l)
            if match:
                ifaces[last_if]["description"] = match.group("descr")
                continue
            # inet
            match = self.rx_inet.search(l)
            if match:
                if match.group("inet") != 'unassigned':
                    ifaces[last_if]["ipv4_addresses"] += [match.group("inet")]
                continue
            # Mac-address
            match = self.rx_mac.search(l)
            if match:
                ifaces[last_if]["mac"] = match.group("mac")
                continue
            # MTU
            match = self.rx_mtu.search(l)
            if match:
                ifaces[last_if]["mtu"] = match.group("mtu")
                continue

        # Process subinterfaces
        for iface in ifaces:
            subif = {
                "name": iface,
                "description" : "",
                "admin_status" : "",
                "oper_status": "",
                "enabled_afi" : [],
                "tagged_vlans" : [],
                "untagged_vlan" : ""
                }
            subif["description"] = ifaces[iface]["description"]
            subif["admin_status"] = ifaces[iface]["admin_status"]
            subif["oper_status"] = ifaces[iface]["oper_status"]
            for vlan in vlan_set:
                if iface in vlan.get("tag_ports"):
                    subif["tagged_vlans"] += [vlan.get("id")]
                if iface in vlan.get("untag_ports") or iface in vlan.get("pvid_ports"):
                    subif["untagged_vlan"] = vlan.get("id")
            if subif["name"] != "" or subif["untagged_vlan"] != "":
                if subif["name"].startswith("vlan"):
                    subif["enabled_afi"] += ['IPv4']
                else:
                    subif["enabled_afi"] += ['BRIDGE']
            if subif["tagged_vlans"] == []: 
                del subif["tagged_vlans"]
            if subif["untagged_vlan"] == "": 
                del subif["untagged_vlan"]
            if ifaces[iface]["ipv4_addresses"] == []:
                del ifaces[iface]["ipv4_addresses"]
            else:
                subif["ipv4_addresses"] = ifaces[iface]["ipv4_addresses"]
                del ifaces[iface]["ipv4_addresses"]
            if ifaces[iface].has_key("mtu"):
                subif["mtu"] = ifaces[iface]["mtu"]
            ifaces[iface]["subinterfaces"] += [subif]
        # Process LACP aggregated links 
        for l in self.cli("show lacp internal").splitlines():
            match = self.rx_lag.search(l)
            if match:
                last_lag = match.group("lag")
            match = self.rx_lag_member.search(l)
            if match:
                ifaces[match.group("lag_member")]["enabled_protocols"] += ['LACP']
                ifaces[match.group("lag_member")]["aggregated_interface"] = 'smartgroup' + last_lag
                
        return [{"interfaces": ifaces.values() }]

    def type_by_name(self, name):
        if name.startswith("gei"):
            return "physical"
        elif name.startswith("xgei"):
            return "physical"
        elif name.startswith("smartgroup"):
            return "aggregated"
        elif name.startswith("lo"):
            return "loopback"
        elif name.startswith("vlan"):
            return "SVI"
        elif name.startswith("null"):
            return "null"
        else:
            raise Exception("Cannot detect interface type for %s" % name)

    def get_si(self, si):
        if si["ipv4_addresses"]:
            si["ipv4_addresses"] = list(si["ipv4_addresses"])
            si["enabled_afi"] += ["IPv4"]
        else:
            del si["ipv4_addresses"]
        return si

    def split_data_in_table_to_columns(self, rows):
        # For each row based on title column width calculate data width
        # After that add data from splitted rows to certain columns.
        rx_head = re.compile(r"^(?P<vlan_id>VLAN\s+)"
                             r"(?P<vlan_name>Name\s+)"
                             r"(?P<pvid_ports>PvidPorts\s+)"
                             r"(?P<untag_ports>UntagPorts\s+)"
                             r"(?P<tag_ports>TagPorts\s+)")
        rx_horizontal_rule = re.compile(r"-{79}")
        rx_spaces = re.compile(r"\s+")
        vl = {
            "id" : [],
            "name" : [],
            "pvid_ports" : [],
            "untag_ports" : [],
            "tag_ports" : []
        }
        vlan_list=[]
        for line in rows:
            match_head = rx_head.search(line)
            match_horizontal_rule = rx_horizontal_rule.search(line)
            if match_head:
                vlan_id_len = len(match_head.group("vlan_id"))
                vlan_name_len = len(match_head.group("vlan_name"))
                pvid_ports_len = len(match_head.group("pvid_ports"))
                untag_ports_len = len(match_head.group("untag_ports"))
                tag_ports_len = len(match_head.group("tag_ports"))+4 # Add 4 to last column to compensate trail spaces
            elif match_horizontal_rule:
                continue
            else:
                shift = 0
                if rx_spaces.sub('',''.join(line[shift:vlan_id_len+shift])) != '':
                    if not vl["id"] == []:
                        vlan_list.append(copy.deepcopy(vl))
                    vl["id"] = line[shift:vlan_id_len+shift]
                    shift += vlan_id_len
                    vl["name"] = line[shift:vlan_name_len+shift]
                    shift += vlan_name_len
                    vl["pvid_ports"] = line[shift:pvid_ports_len+shift]
                    shift += pvid_ports_len
                    vl["untag_ports"] = line[shift:untag_ports_len+shift]
                    shift += untag_ports_len
                    vl["tag_ports"] = line[shift:tag_ports_len+shift]
                else:
                    vl["id"] += line[shift:vlan_id_len+shift]
                    shift += vlan_id_len
                    vl["name"] += line[shift:vlan_name_len+shift]
                    shift += vlan_name_len
                    vl["pvid_ports"] += line[shift:pvid_ports_len+shift]
                    shift += pvid_ports_len
                    vl["untag_ports"] += line[shift:untag_ports_len+shift]
                    shift += untag_ports_len
                    vl["tag_ports"] += line[shift:tag_ports_len+shift]
        vlan_list.append(copy.deepcopy(vl))
        return vlan_list

    def split_interface_groups(self, data):
        #desassembly interface groupping
        rx_interface_group = re.compile(r"^(?P<int_group>.+(?:group|\/))(?P<first_num>\d+)-(?P<last_num>\d+)$")
        result = []
        for interface in data:
            match = rx_interface_group.search(interface)
            if match:
                step=0
                for interface_group in range(int(match.group("first_num"))-1,int(match.group("last_num"))):
                    result.append(match.group("int_group")+str(int(match.group("first_num"))+step))
                    step=step+1
            else:
                result.append(interface)
        return result

    def split_interface(self, data):
        rx_spaces = re.compile(r"\s+")
        result = rx_spaces.sub('',''.join(data)).split(',')
        return result

    def reformat_vlans(self, data):
        rx_spaces = re.compile(r"\s+")
        vlan_list = []
        for vl in data:
            vl["id"] = int(rx_spaces.sub('',''.join(vl["id"])))
            vl["name"] = rx_spaces.sub('',''.join(vl["name"]))
            vl["tag_ports"]=self.split_interface(vl["tag_ports"])
            vl["pvid_ports"]=self.split_interface(vl["pvid_ports"])
            vl["untag_ports"]=self.split_interface(vl["untag_ports"])
            vl["pvid_ports"]=self.split_interface_groups(vl["pvid_ports"])
            vl["tag_ports"]=self.split_interface_groups(vl["tag_ports"])
            vl["untag_ports"]=self.split_interface_groups(vl["untag_ports"])
            vlan_list.append(copy.deepcopy(vl))
        return vlan_list
    
    def get_vlan(self, data):
        vlans = self.split_data_in_table_to_columns(data)
        self.reformat_vlans(vlans)
        return vlans
