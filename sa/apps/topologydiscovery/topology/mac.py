# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Topology Discovery
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from __future__ import with_statement
from base import *
import types

class Cloud(Node):
    dot_shape="circle"

class MACTopology(Topology):
    def __init__(self,data,hints=[],per_vlan=None):
        self.per_vlan=per_vlan
        super(MACTopology,self).__init__(data,hints)
    ##
    ## Create topology nodes
    ##
    def create_nodes(self,data,hints=[]):
        interface_macs=Counter() # (object,interface)->count
        mac_interfaces={} # mac_label ->[(object,interface)]
        for obj,d in data:
            # Check mac data present
            if not d["has_mac"]:
                continue
            o=Object(self,obj)
            cn=0 # Cloud number
            for r in d["mac"]:
                vlan_id=r["vlan_id"]
                # Filter VLAN for per_vlan mode
                if self.per_vlan and vlan_id!=self.per_vlan:
                    continue
                #
                mac=r["mac"]
                interface=r["interfaces"][0]
                mac_label="%d:%s"%(vlan_id,mac)
                # Update interface macs
                interface_macs.update((o,interface))
                # Update mac_interfaces
                try:
                    mac_interfaces[mac_label]+=[(o,interface)]
                except KeyError:
                    mac_interfaces[mac_label]=[(o,interface)]
        # Create clouds
        cn=0 # Cloud number
        seen_hashes=set()
        for m,I in mac_interfaces.items():
            if len(I)==1:
                continue # Skip mac if only seen at single interface
            # Serialize interfaces list to hash
            h=",".join(sorted(["%s:%s"%(id(o),i) for o,i in I]))
            # Check cloud not seen yet
            if h in seen_hashes:
                continue
            seen_hashes.add(h)
            #
            c=Cloud(self,"Cloud #%d"%cn)
            cn+=1
            for o,i in I:
                if interface_macs[(o,i)]==1: # Is access interface
                    c.connect(o) # Connect cloud to access interface
                else:
                    o.connect(c,i) # Connect interface to cloud
        # Remove duplicated clouds
        seen_hashes=set()
        for c in self.all_clouds():
            h=",".join(sorted(["%s:%s"%(id(o),i) for o,i in c.connected]))
            if c.connections:
                h+="->"+",".join(sorted(["%s:%s"%(id(o),i) for o,i in c.connections]))
            if h in seen_hashes:
                c.delete()
                continue
            seen_hashes.add(h)
    ##
    ## All Clouds in topology
    ##
    def all_clouds(self):
        return Cloud.filter(self.objects.values())
    ##
    ##
    ##
    def has_backpath(self,o1,o2,exclude=set(),seen=set()):
        for ro,i in o1.connected:
            if ro==o2 and i not in exclude:
                return True
        for ro,i in o1.connected:
            if ro not in seen and ro!=o2 and self.has_backpath(ro,o2,exclude,seen|set([o1])):
                return True
        return False
    ##
    ## Discovery
    ##
    def discover(self):
        def in_path(o1,o2):
            try:
                O=backrefs[o1]&backrefs[o2]
            except KeyError:
                return None
            m=set()
            for o3 in O:
                if o1 in refs[o3] and o2 in refs[o3]:
                    i1=refs[o3][o1]
                    i2=refs[o3][o2]
                    if i1!=i2:
                        m.add((i1,o3,i2))
            if m:
                if len(m)==1:
                    return m.pop()
                else:
                    return m
            return None
        
        objects=self.all_objects()
        l_objects=len(objects)
        self.l_netkey=l_objects*(l_objects-1)/2
        # Detect interfaces leading outside of topology
        for o in self.all_objects():
            left=o.interfaces()
            ic=Counter()
            for ro,i in o.connections:
                ic.update(i)
                if len(ro.connections)>0 and i in left:
                    left.remove(i)
            # Check backpaths
            for ro,i in o.connections:
                if i in left:
                    if ic[i]==1 or self.has_backpath(ro,o,left):
                        # Backpath found
                        # Reverse all edges with outside interface
                        for ro,ri in list(o.connections):
                            if ri==i:
                                ro.disconnect(o,i)
                                ro.connect(o)
                        break
        # Build constraints
        # o1[o2]=i1
        refs={}
        backrefs={}
        for o in self.all_objects():
            for co,i in o.connections:
                if len(co.connections)==1:
                    ro=list(co.connections)[0][0]
                    if o not in refs:
                        refs[o]={}
                    refs[o][ro]=i
                    if ro not in backrefs:
                        backrefs[ro]=set()
                    backrefs[ro].add(o)
        # Build skeleton paths
        paths={}
        for o1 in refs:
            for o2 in refs[o1]:
                SP=[(None,o1,refs[o1][o2])]
                m=in_path(o1,o2)
                if m:
                    SP+=[m]
                # Try to reverse last interface
                last_i=None
                if o2 in refs:
                    if o1 in refs[o2]: # direct reference
                        last_i=refs[o2][o1]
                if last_i is None:
                    # Finally, try a single interface
                    interfaces=o2.interfaces()
                    if len(interfaces)==1:
                        last_i=list(interfaces)[0]
                SP+=[(last_i,o2,None)]
                paths[o1,o2]=SP
        # Refine paths
        not_refined=True
        while not_refined:
            not_refined=False
            # Refine with references
            for P in paths.keys():
                path=paths[P]
                np=[path.pop(0)]
                for p in path:
                    last=np[-1]
                    if type(p)==types.TupleType and type(last)==types.TupleType:
                        # Try to find path between
                        _,o1,_=last
                        _,o2,_=p
                        m=in_path(o1,o2)
                        if m:
                            np+=[m]
                            not_refined=True
                    elif type(p)!=types.TupleType and type(last)==types.TupleType:
                        # Try to split first element
                        while p:
                            for pp in p:
                                _,o1,i1=pp
                                first=True
                                for ppp in p-set([pp]):
                                    i2,o2,_=ppp
                                    if not o1 in refs or o2 not in refs[o1] or refs[o1][o2]!=i1:
                                        first=False
                                        break
                                if first:
                                    break
                            if first:
                                np+=[pp]
                                p=p-set([pp])
                                not_refined=True
                            else:
                                break
                        if len(p)==1:
                            p=p.pop()
                    if p:
                        np+=[p]
                paths[P]=np
            # Enrich existing skeleton paths with know paths
            for P in paths.keys():
                path=paths[P]
                np=[path.pop(0)]
                for p in path:
                    last=np[-1]
                    if type(p)==types.TupleType and type(last)==types.TupleType:
                        _,o1,_=last
                        _,o2,_=p
                        if (o1,o2) in paths and len(paths[o1,o2])>2:
                            np+=paths[o1,o2][1:-1]
                            not_refined=True
                    np+=[p]
                paths[P]=np
        for path in paths.values():
            last=path.pop(0)
            for p in path:
                if type(last)==types.TupleType and type(p)==types.TupleType:
                    _,o1,i1=last
                    i2,o2,_=p
                    yield o1.managed_object,i1 if i1 else "?",o2.managed_object,i2 if i2 else "?"
                last=p
        