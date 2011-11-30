# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generic.get_topology_data
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
from __future__ import with_statement
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetTopologyData


class Script(NOCScript):
    """
    Retrieve data for topology discovery
    """
    name = "Generic.get_topology_data"
    implements = [IGetTopologyData]
    requires = []

    def execute(self, get_mac=False, get_arp=False, get_lldp=False,
                get_stp=False, get_cdp=False, get_fdp=False,
                get_interfaces=False):
        data = {
            "has_mac": False,
            "mac": None,
            "has_arp": False,
            "arp": None,
            "has_lldp": False,
            "lldp_neighbors": None,
            "has_cdp": False,
            "cdp_neighbors": None,
            "has_fdp": False,
            "fdp_neighbors": None,
            "has_stp": False,
            "stp": None,
            "portchannels": [],
            "has_interfaces": False,
            "interfaces": None
            }
        x_list = (self.CLISyntaxError, self.NotSupportedError,
                  self.UnexpectedResultError)
        with self.cached():
            # get mac addresses
            if get_mac and self.scripts.has_script("get_mac_address_table"):
                with self.ignored_exceptions(x_list):
                    mac_data = self.scripts.get_mac_address_table()
                    if mac_data:
                        data["has_mac"] = True
                        data["mac"] = mac_data
                # Get ARP cache
                if get_arp and self.scripts.has_script("get_arp"):
                    with self.ignored_exceptions(x_list):
                        arp_data = self.scripts.get_arp()
                        if arp_data:
                            data["has_arp"] = True
                            data["arp"] = arp_data
            # get lldp neighbors
            if get_lldp:
                if self.scripts.has_script("get_chassis_id"):
                    with self.ignored_exceptions(x_list):
                        data["chassis_id"] = self.scripts.get_chassis_id()
                if self.scripts.has_script("get_lldp_neighbors"):
                    with self.ignored_exceptions(x_list):
                        lldp_neighbors = self.scripts.get_lldp_neighbors()
                        if lldp_neighbors:
                            data["has_lldp"] = True
                            data["lldp_neighbors"] = lldp_neighbors
            # get cdp neighbors
            if get_cdp:
                if self.scripts.has_script("get_cdp_neighbors"):
                    with self.ignored_exceptions(x_list):
                        cdp_neighbors = self.scripts.get_cdp_neighbors()
                        if cdp_neighbors:
                            data["has_cdp"] = True
                            data["cdp_neighbors"] = cdp_neighbors
            # get fdp neighbors
            if get_fdp:
                if self.scripts.has_script("get_fdp_neighbors"):
                    with self.ignored_exceptions(x_list):
                        fdp_neighbors = self.scripts.get_fdp_neighbors()
                        if fdp_neighbors:
                            data["has_fdp"] = True
                            data["fdp_neighbors"] = fdp_neighbors
            # Get STP data
            if get_stp:
                if self.scripts.has_script("get_spanning_tree"):
                    with self.ignored_exceptions(x_list):
                        stp = self.scripts.get_spanning_tree()
                        data["has_stp"] = stp["mode"] != "None"
                        data["stp"] = stp
            # get portchannels
            if self.scripts.has_script("get_portchannel"):
                with self.ignored_exceptions(x_list):
                    data["portchannels"] = self.scripts.get_portchannel()
            # get interfaces
            if get_interfaces:
                if "get_interfaces" in self.scripts:
                    with self.ignored_exceptions(x_list):
                        interfaces = self.scripts.get_interfaces()
                        data["has_interfaces"] = bool(interfaces)
                        data["interfaces"] = interfaces
        return data
