# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Topology Discovery
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from mac import MACTopology
from lldp import LLDPTopology

class TopologyDiscovery(object):
    ##
    ## data is a list of (managed_object,IGetTopologyData)
    ##
    def __init__(self,data,mac=True,per_vlan_mac=False,lldp=True):
        #
        self.links=[] # (object,interface,object_interface)
        self.links_methods={} # (o,i,o,i) -> method
        self.objects=set()
        self.object_interfaces={} # o-> interfaces list
        # Find objects
        for o,d in data:
            self.objects.add(o)
        # MAC address topology discovery
        if mac:
            # Prepare for MAC topology discovery
            if per_vlan_mac:
                # Perform discovery for each VLAN separately
                vlans=set()
                for o,d in data:
                    if d["has_mac"] and d["mac"]:
                        # Find all vlans
                        for r in d["mac"]:
                            vlans.add(r["vlan_id"])
                # Buld data and perform discovery per each vlan
                for vlan in vlans:
                    vd=[]
                    for o,d in data:
                        vlan_macs=[r for r in d["mac"] if r["vlan_id"]==vlan]
                        if vlan_macs:
                            vd+=[(o,vlan_macs)]
                    # Perform discovery
                    t=MACTopology(vd)
                    for R in t.discover():
                        self.add_link(R,"mac vlan %d"%vlan)
            else:
                # Perform discovery for common tree
                t=MACTopology([(o,r["mac"]) for o,r in data])
                for R in t.discover():
                    self.add_link(R,"mac")
                t.dot("mac")
        # LLDP Topology discovery
        if lldp:
            t=LLDPTopology(data)
            for R in t.discover():
                self.add_link(R,"lldp")
    ##
    ## Add discovered link
    ##
    def add_link(self,R,method):
        o1,i1,o2,i2=R
        RR=(o2,i2,o1,i1)
        if R not in self.links and RR not in self.links:
            self.links+=[R]
            self.add_interface(o1,i1)
            self.add_interface(o2,i2)
            try:
                self.links_methods[R]+=[method]
            except KeyError:
                self.links_methods[R]=[method]
    ##
    def add_interface(self,o,i):
        try:
            self.object_interfaces[o]+=[i]
        except KeyError:
            self.object_interfaces[o]=[i]
    ##
    ## Render graphviz DOT with topology
    ##
    def dot(self):
        def q_interface(s):
            return s.replace(" ","").replace("/","")
        r=["graph {"]+["node [shape=Mrecord]"]+["rankdir=RL;"]
        for o in self.objects:
            r+=["\"%s\" [label=\"%s|%s|%s\"];"%(o.id,o.name,o.profile_name,"|".join(["<%s> %s"%(q_interface(i),i.replace(" ","\\ ")) for i in sorted(self.object_interfaces.get(o,[]))]))]
        for o1,i1,o2,i2 in self.links:
            r+=["%s:%s -- %s:%s;"%(o1.id,q_interface(i1),o2.id,q_interface(i2))]
        r+=["}"]
        return "\n".join(r)
