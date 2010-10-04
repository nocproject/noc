# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Topology Discovery
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from __future__ import with_statement
from base import *
import types,pprint,itertools

## Set up itertools
if hasattr(itertools,"combinations"):
    # Python 2.6 or later
    combinations=itertools.combinations
else:
    ##
    ## Pure-python replacement for Python 2.5
    ##
    def combinations(s,n=None):
        ss=s[:]
        while ss:
            c=ss.pop(0)
            for cc in ss:
                yield (c,cc)
    

class Cloud(Node):
    dot_shape="circle"
    c=itertools.count()
    def __init__(self,topology,name):
        if "%(number)s" in name:
            name=name%{"number":self.c.next()}
        super(Cloud,self).__init__(topology,name)


##
## FIB encapsupation
##
class FIB(object):
    def __init__(self):
        self.fib={} # (o1,o2) -> interface
    
    ##
    ## Add path to FIB
    ##
    def add(self,o1,o2,interface):
        self.fib[o1,o2]=interface
    
    ##
    ## Lookup FIB for path.
    ## Returns interface or None, if not path found
    ##
    def lookup(self,o1,o2):
        try:
            return self.fib[o1,o2]
        except KeyError:
            return None
    
##
## MAC-adress-based discovery
##
class MACTopology(Topology):
    def __init__(self,data,hints=[],per_vlan=None):
        self.per_vlan=per_vlan
        self.interface_macs=Counter() # (object,interface)-> mac cound
        self.mac_interfaces={}        # mac_label -> [(object,interface)]
        self.object_addresses={}      # ip -> object
        self.object_macs={}           # mac -> object
        self.object_map={}            # managed object -> object
        self.arp_seen=set()           # (object,interface,remote object)
        self.fib=FIB()                
        self.skeleton_paths={}        # (o1,o2) -> path
        super(MACTopology,self).__init__(data,hints)
    
    ##
    ## Create Object nodes
    ##
    def create_objects(self,data):
        for obj,d in data:
            if not d["has_mac"]:
                continue
            o=Object(self,obj)
            self.object_addresses[obj.address]=o
            self.object_map[obj]=o
    
    ##
    ## Process ARP Cache
    ##
    def process_arp_cache(self,data):
        for obj,d in data:
            if not d["has_mac"] or not d["has_arp"]:
                continue
            mac_interface={} # MAC -> interface
            for r in d["mac"]:
                mac_interface[r["mac"]]=r["interfaces"][0]
            #
            o=self.object_map[obj]
            for r in d["arp"]:
                ip=r["ip"]
                mac=r["mac"]
                if ip in self.object_addresses:
                    ro=self.object_addresses[ip]
                    if mac not in self.object_macs:
                        # Set up object_macs
                        self.object_macs[mac]=ro
                    # Resolve ARP interface via MAC database
                    # (Some swithces report SVI in ARP, instead of port)
                    if mac in mac_interface:
                        self.arp_seen.add((o,mac_interface[mac],ro))
    
    ##
    ## Process MAC Database
    ##
    def process_mac_interfaces(self,data):
        for obj,d in data:
            if not d["has_mac"]:
                continue
            for r in d["mac"]:
                vlan_id=r["vlan_id"]
                # Filter vlans for PVST
                if self.per_vlan and vlan_id!=self.per_vlan:
                    continue
                mac=r["mac"]
                # Skip MACs known to belong to object
                if mac in self.object_macs:
                    continue
                o=self.object_map[obj]
                interface=r["interfaces"][0]
                mac_label="%d:%s"%(vlan_id,mac)
                # Update interface macs count
                self.interface_macs.update((o,interface))
                # Update mac_interfaces
                try:
                    self.mac_interfaces[mac_label]+=[(o,interface)]
                except KeyError:
                    self.mac_interfaces[mac_label]=[(o,interface)]
    
    ##
    ## Create Cloud nodes
    ##
    def create_clouds(self):
        # Create clouds for ARP records
        for o1,i1,o2 in self.arp_seen:
            c=Cloud(self,"#%(number)s (ARP)")
            o1.connect(c,i1)
            c.connect(o2)
        # Create clouds for MAC -> interface mappings
        seen=set()
        for m,I in self.mac_interfaces.items():
            if len(I)==1:
                # Skip MAC if seen only at single interface, as no topology knowledge within
                continue
            # Serialize interface list to hash
            h="\n".join(sorted(["%s:%s"%(id(o),i) for o,i in I]))
            # Check cloud is not seen before
            if h in seen:
                continue # Do not create duplicated cloud
            seen.add(h)
            # Create cloud
            c=Cloud(self,"#%(number)s")
            for o,i in I:
                if self.interface_macs[o,i]==1:
                    # Only one MAC on interface. Treat as access interface
                    # Connect cloud to object with access interface
                    c.connect(o)
                else:
                    # Connect interface to cloud
                    o.connect(c,i)
        # Finally check clouds and remove duplicates
        seen=set()
        for c in self.all_clouds():
            h="\n".join(sorted(["%s:%s"%(id(o),i) for o,i in c.connected]))+"\n---\n"+"\n".join(sorted(["%s:%s"%(id(o),i) for o,i in c.connections]))
            if h in seen:
                # Remove duplicates
                c.delete()
                continue
            seen.add(h)
    
    ##
    ## Prepare FIB and reverse FIB
    ##
    def build_fib(self):
        for o in self.all_objects():
            for co,i in o.connections:
                if len(co.connections)==1:
                    ro=list(co.connections)[0][0]
                    if o==ro:
                        continue # Strip loops
                    self.fib.add(o,ro,i)
    
    ##
    ## Create topology nodes from data
    ##
    def create_nodes(self,data,hints=[]):
        self.create_objects(data)
        self.process_arp_cache(data)
        self.process_mac_interfaces(data)
        self.create_clouds()
    
    ##
    ## All Clouds in topology
    ##
    def all_clouds(self):
        return Cloud.filter(self.objects.values())
    
    ##
    ## <?>
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
    ## Detect interfaces leading outside of topology
    ## and reconnect the clouds. Do not produces duplicated cloud
    ##
    def reverse_egress_interfaces(self):
        for o in self.all_objects():
            egress=o.interfaces()
            ic=Counter() # Interface -> number of cluds connected to
            # Detect egress interfaces
            for ro,i in o.connections:
                ic.update(i)
                if len(ro.connections)>0 and i in egress:
                    # Interface connected to cloud, which connected to another object
                    # cannot be egress interface
                    egress.remove(i)
            # Check backpaths to egress interfaces
            for ro,i in o.connections:
                if i in egress and (ic[i]==1 or self.has_backpath(ro,o,egress)):
                    # Backpath found
                    # Reverse all edges with egress interface
                    for ro,ri in list(o.connections):
                        if ri==i:
                            # Swap edge direction
                            ro.disconnect(o,i)
                            ro.connect(o)
                    break
    
    ##
    ## Returns True if o3 is on a path o1-o2
    ##
    def is_on_path(self,o1,o2,o3):
        i=self.fib.lookup(o3,o1)
        j=self.fib.lookup(o3,o2)
        return i is not None and j is not None and i!=j
    
    ##
    ## Returns true if path o3-o4 is closed within o1-o2
    ##
    def is_inner_path(self,o1,o2,o3,o4):
        return self.is_on_path(o1,o2,o3) and self.is_on_path(o1,o2,o4)
    
    ##
    ## Build minimal set of skeleton paths.
    ## Skeleton path is a list of (ingress interface,object,egress interface)
    ## Where list order define precidence.
    ## Set means "all in not specific order"
    ##
    def build_skeleton_paths(self):
        # Find minimal set of skeleton paths
        # Such as no path closed within another
        for o1,o2 in combinations(self.all_objects(),2):
            # Check o1 knows about o2 and vise versa
            if self.fib.lookup(o1,o2) is None or self.fib.lookup(o2,o1) is None:
                continue
            to_add=True
            for o3,o4 in self.skeleton_paths.keys():
                # Check if o1-o2 covers existing skeleton path
                if self.is_inner_path(o1,o2,o3,o4):
                    del self.skeleton_paths[o3,o4] # Delete inner path
                # Check if o1-o2 is inner path of existing one
                elif self.is_inner_path(o3,o4,o1,o2):
                    to_add=False
                    break
            if to_add:
                self.skeleton_paths[o1,o2]=None # Add a stub to mark skeleton path candidate
        # Build initial skeleton path set
        for o1,o2 in self.skeleton_paths:
            sp=[(None,o1,self.fib.lookup(o1,o2))] # Starting node
            # Install all objects on path
            s=set()
            for o3 in self.all_objects():
                i1=self.fib.lookup(o3,o1)
                i2=self.fib.lookup(o3,o2)
                if i1 is not None and i2 is not None and i1!=i2:
                    s.add((i1,o3,i2))
            if s:
                # If only one object in path - unroll to list
                if len(s)==1:
                    s=s.pop()
                sp+=[s]
            sp+=[(self.fib.lookup(o2,o1),o2,None)] # Tailing node
            self.skeleton_paths[o1,o2]=sp
    
    ##
    ##
    ##
    def refine_paths_order(self):
        ##
        ## Try to split first and last elements of subset U on path o1-o2
        ##
        def resolve_first_or_last(o1,o2,U):
            for a in U:
                first=True
                last=True
                for b in U:
                    if a==b:
                        continue
                    bi=self.fib.lookup(b,o1)
                    bia=self.fib.lookup(b,a)
                    if bia is None:
                        first=False
                        last=False
                        break
                    if bi==bia:
                        # Directing to head, cannot be last
                        last=False
                    else:
                        # Directing to tail, cannot be first
                        first=False
                    if not first and not last:
                        break # Try another
                if first:
                    return [a,U-set([a])]
                elif last:
                    return [U-set([a]),a]
            # Cannot align subset
            return None
        #
        changed=False
        for o1,o2 in self.skeleton_paths:
            path=self.skeleton_paths[o1,o2]
            np=[]
            for p in path:
                if type(p)==types.TupleType:
                    # Already resolved
                    np+=[p]
                else:
                    # Try to resolve order as deep as possible
                    tail=[]
                    while True:
                        n=resolve_first_or_last(o1,o2,p)
                        if n is None:
                            np+=[p]+tail
                            break
                        else:
                            x,y=n
                            changed=True
                            if type(x)==types.TupleType:
                                # Resolved first element
                                np+=[x]
                                n=y
                            else:
                                # Resolved last element
                                n=x
                                tail+=[y]
            if len(path)>len(np):
                raise Exception("Path lost")
            self.skeleton_paths[o1,o2]=np
        return changed
    
    ##
    ## Try to refine paths pairs if both paths starting from same node
    ##
    def refine_coaligned_paths(self):
        changed=False
        for o1,o2 in self.skeleton_paths:
            for oo1,o3 in self.skeleton_paths:
                if o1!=oo1 or o2==o3:
                    continue
                # o1-o2, o1-o3 -- pair of paths with common start
                p2=self.skeleton_paths[o1,o2]
                p3=self.skeleton_paths[o1,o3]
                np2=[]
                np3=[]
                lp2=len(p2)
                lp3=len(p3)
                while p2 and p3:
                    a2=p2.pop(0)
                    a3=p3.pop(0)
                    if a2==a3:
                        # Same element, left in place
                        np2+=[a2]
                        np3+=[a2]
                    else:
                        # Difference found
                        if type(a2)!=types.TupleType and type(a3)!=types.TupleType:
                            # Both are unresolved sets, split
                            u0=a2&a3 # Common part
                            u2=a2-u0 # Rest parts
                            u3=a3-u0 # Rest parts
                            # Install common part
                            if u0:
                                if len(u0)==1:
                                    u0=u0.pop()
                                np2+=[u0]
                                np3+=[u0]
                            # Install parts left
                            if u2:
                                if len(u2)==1:
                                    u2=u2.pop()
                                np2+=[u2]
                            if u3:
                                if len(u3)==1:
                                    u3=u3.pop()
                                np3+=[u3]
                            # Install tail
                            np2+=p2
                            np3+=p3
                            changed=True
                            break
                        else:
                            # Direction changed
                            np2+=[a2]+p2
                            np3+=[a3]+p3
                            break
                if lp2>len(np2) or lp3>len(np3):
                    raise Exception("Path lost")
                self.skeleton_paths[o1,o2]=np2
                self.skeleton_paths[o1,o3]=np3
        return changed
    
    ##
    ## Returns resolved links
    ##
    def get_links(self):
        links=set()
        for o1,o2 in self.skeleton_paths:
            path=self.skeleton_paths[o1,o2]
            last=path.pop(0)
            while path:
                p=path.pop(0)
                if type(p)==types.TupleType:
                    _,o1,i1=last
                    i2,o2,_=p
                    links.add((o1.managed_object,i1,o2.managed_object,i2))
                    last=p
                    continue
                else:
                    # Skip unresolved parts until tuple found
                    while path:
                        last=path.pop(0)
                        if type(last)==types.TupleType:
                            break
        return links
    
    ##
    ##
    ##
    def dump_skeleton_paths(self):
        unresolved=0
        for o1,o2 in self.skeleton_paths:
            print o1,o2,":"
            r=[]
            for p in self.skeleton_paths[o1,o2]:
                if type(p)==types.TupleType:
                    r+=[str(p)]
                else:
                    unresolved+=1
                    r+=["{ %s }"%",".join([str(s) for s in p])]
            print "    "," - ".join([x.replace("Object ","") for x in r])
        print
        print "Unresolved subsets",unresolved
    
    ## Discovery process.
    ## Generator returning resolved links
    ##
    def discover(self):
        self.reverse_egress_interfaces()
        self.build_fib()
        self.build_skeleton_paths()
        while True:
            if      not self.refine_paths_order()\
                and not self.refine_coaligned_paths(): # TODO: refine paths ending in same node
                break
        # Return links
        for l in self.get_links():
            yield l
    