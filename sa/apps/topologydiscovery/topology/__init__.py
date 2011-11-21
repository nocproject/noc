# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Topology Discovery
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from mac import MACTopology
from lldp import LLDPTopology
from cdp import CDPTopology
from fdp import FDPTopology
from stp import STPTopology


class Link(object):
    def __init__(self, topology, o1, i1, o2, i2, portchannel_link=None):
        self.topology = topology
        self.o1 = o1
        self.i1 = i1
        self.o2 = o2
        self.i2 = i2
        self.i1_prefix = ""
        self.i2_prefix = ""
        self.methods = set()
        self.is_portchannel = (o1 in self.topology.portchannels and
                               i1 in self.topology.portchannels[o1] and
                               o2 in self.topology.portchannels and
                               i2 in self.topology.portchannels[o2])
        self.details = []
        self.portchannel_link = portchannel_link
        self.n_links = len(
            self.topology.portchannels[o1][i1]) if self.is_portchannel else 0
        # Add to portchannel
        if self.portchannel_link:
            self.portchannel_link.details += [self]
            self.i1_prefix = self.portchannel_link.i1 + ": "
            self.i2_prefix = self.portchannel_link.i2 + ": "
        # Set up topology index
        self.topology.links += [self]
        self.add_interface(o1, i1)
        self.add_interface(o2, i2)

    def __repr__(self):
        return "%s:%s -- %s:%s" % (self.o1, self.i1, self.o2, self.i2)

    def add_interface(self, o, i):
        try:
            self.topology.object_links[o] += [self]
        except KeyError:
            self.topology.object_links[o] = [self]
        try:
            if i not in self.topology.object_interfaces[o]:
                self.topology.object_interfaces[o] += [i]
        except KeyError:
            self.topology.object_interfaces[o] = [i]

    def match(self, o1, i1, o2, i2):
        return ((self.o1 == o1 and self.i1 == i1
                and self.o2 == o2 and self.i2 == i2) or
                (self.o1 == o2 and self.i1 == i2 and
                 self.o2 == o1 and self.i2 == i1))

    def unresolved_link_count(self):
        """
        Returns a number of unresolved links
        :return:
        """
        return self.n_links - len(self.details)


class TopologyDiscovery(object):
    ##
    ## data is a list of (managed_object,IGetTopologyData)
    ##
    def __init__(self, data, mac=True, per_vlan_mac=False, arp=True, lldp=True,
                 stp=True, cdp=False, fdp=False, mac_port_bindings=False):
        #
        self.links = []  # List of Link
        self.object_links = {}  # object->link
        self.objects = set()
        self.object_interfaces = {}       # o -> interfaces list
        self.portchannels = {}            # o -> portchannel -> members
        self.portchannel_interfaces = {}  # o -> interface -> portchannel
        self.mac_bindings = []            # (object, interface, mac, ip)
        # Find objects
        for o, d in data:
            # Populate objects
            self.objects.add(o)
            # Populate portchannels
            if "portchannels" in d and d["portchannels"]:
                self.portchannels[o] = {}
                self.portchannel_interfaces[o] = {}
                for p in d["portchannels"]:
                    self.portchannels[o][p["interface"]] = p["members"]
                    for m in p["members"]:
                        self.portchannel_interfaces[o][m] = p["interface"]
        # MAC address topology discovery
        if mac:
            # Prepare for MAC topology discovery
            if per_vlan_mac:
                # Perform discovery for each VLAN separately
                vlans = set()
                for o, d in data:
                    if d["has_mac"] and d["mac"]:
                        # Find all vlans
                        for r in d["mac"]:
                            vlans.add(r["vlan_id"])
                # Buld data and perform discovery per each vlan
                if mac_port_bindings:
                    self.mac_port_bindings = []
                for vlan in vlans:
                    vd = []
                    for o, d in data:
                        vlan_macs = [r for r in d["mac"] if
                                     r["vlan_id"] == vlan]
                        if vlan_macs:
                            dd = d.copy()
                            dd["mac"] = vlan_macs
                            vd += [(o, dd)]
                    # Perform discovery
                    t = MACTopology(vd)
                    for R in t.discover():
                        self.add_link(R, "MAC%d" % vlan)
                    if mac_port_bindings:
                        self.mac_port_bindings += list(
                            t.get_mac_port_bindings())
            else:
                # Perform discovery for common tree
                t = MACTopology(data)
                for R in t.discover():
                    self.add_link(R, "MAC")
                t.dot("mac")
                if mac_port_bindings:
                    self.mac_port_bindings = list(t.get_mac_port_bindings())
        # LLDP Topology discovery
        if lldp:
            t = LLDPTopology(data)
            for R in t.discover():
                self.add_link(R, "LLDP")
        # CDP Topology discovery
        if cdp:
            t = CDPTopology(data)
            for R in t.discover():
                self.add_link(R, "CDP")
        # FDP Topology discovery
        if fdp:
            t = FDPTopology(data)
            for R in t.discover():
                self.add_link(R, "FDP")
        # STP Topology discovery
        if stp:
            t = STPTopology(data)
            for R in t.discover():
                self.add_link(R, "STP")
        # Finally collapse all refined portchannels
        self.collapse_refined_portchannels()

    def find_link(self, o1, i1, o2, i2):
        if not o1 in self.object_links or not o2 in self.object_links:
            return False
        for l in self.object_links[o1]:
            if l.match(o1, i1, o2, i2):
                return l
        return None

    def add_link(self, R, method):
        """
        Add discovered link
        :param R:
        :param method:
        :return:
        """
        o1, i1, o2, i2 = R
        in_portchannel = (o1 in self.portchannel_interfaces and
                          i1 in self.portchannel_interfaces[o1] and
                          o2 in self.portchannel_interfaces and
                          i2 in self.portchannel_interfaces[o2])
        l = self.find_link(o1, i1, o2, i2)
        if not l:
            if in_portchannel:
                # Add portchannel itself, if not exists
                pi1 = self.portchannel_interfaces[o1][i1]
                pi2 = self.portchannel_interfaces[o2][i2]
                pl = self.find_link(o1, pi1, o2, pi2)
                if not pl:
                    pl = Link(self, o1, pi1, o2, pi2)
                else:
                    if pl.o1 != o1:
                        # swap
                        x = o1, i1
                        o1, i1 = o2, i2
                        o2, i2 = x
            else:
                pl = None
            l = Link(self, o1, i1, o2, i2, pl)

    def collapse_refined_portchannels(self):
        """
        Collapse refined portchannels
        :return:
        """
        nl = []
        # Resolve portchannels with only one unresolved link
        for l in [l for l in self.links if
                  l.is_portchannel and l.unresolved_link_count() == 1]:
            o1set = set(self.portchannels[l.o1][l.i1])
            o2set = set(self.portchannels[l.o2][l.i2])
            for l2 in l.details:
                o1set.remove(l2.i1)
                o2set.remove(l2.i2)
            Link(self, l.o1, o1set.pop(), l.o2, o2set.pop(), l)
        # Remove fully resolved portchannels
        self.links = [l for l in self.links if
                      not l.is_portchannel or l.unresolved_link_count()]
        # Rename partially resolved portchannels
        for l in [l for l in self.links if
                  l.is_portchannel and l.unresolved_link_count() > 1]:
            # Convert interface names
            o1set = set(self.portchannels[l.o1][l.i1])
            o2set = set(self.portchannels[l.o2][l.i2])
            for l2 in l.details:
                o1set.remove(l2.i1)
                o2set.remove(l2.i2)
            l.i1 = l.i1 + ": " + ", ".join(o1set)
            l.i2 = l.i2 + ": " + ", ".join(o2set)
        # Rename interfaces in portchannels
        for l in [l for l in self.links if l.portchannel_link]:
            l.i1 = l.i1_prefix + l.i1
            l.i2 = l.i2_prefix + l.i2
        # Rebuild indexes
        self.object_interfaces = {}
        self.object_links = {}
        for l in self.links:
            l.add_interface(l.o1, l.i1)
            l.add_interface(l.o2, l.i2)

    ##
    rx_interface = re.compile(r"[/:,\-.]")

    def dot(self):
        """
        Render graphviz DOT with topology
        :return:
        """
        def q_interface(s):
            return self.rx_interface.sub("_", s.replace(" ", ""))

        def q_name(i):
            return i.replace(" ", "\\ ")

        r = ["graph {"] + ["node [shape=Mrecord]"] + ["rankdir=RL;"] + [
            "graph [ splines = false ]"]
        for o in self.objects:
            r += ["\"%s\" [label=\"%s|%s|%s\"];" % (
            o.id, o.name, o.profile_name, "|".join(
                ["<%s> %s" % (q_interface(i), q_name(i))
                 for i in sorted(self.object_interfaces.get(o, []))]))]
        for l in self.links:
            r += ["%s:%s -- %s:%s;" % (
            l.o1.id, q_interface(l.i1), l.o2.id, q_interface(l.i2))]
        r += ["}"]
        return "\n".join(r)
