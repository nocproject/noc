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
        try:
            ss=s.copy()
        except AttributeError:
            ss=s[:]
        while ss:
            c=ss.pop()
            for cc in ss:
                yield (c,cc)
    
##
## FIB encapsupation
##
class FIB(object):
    def __init__(self):
        self.fib={} # (o1,o2) -> interface
        self.ifib={} # (o1,interface) -> set of objects
        self.interfaces={} # o -> set of interfaces
    
    ##
    ## Add path to FIB
    ##
    def add(self,o1,o2,interface):
        if (o1,o2) in self.fib:
            return
        self.fib[o1,o2]=interface
        try:
            self.ifib[o1,interface].add(o2)
        except KeyError:
            self.ifib[o1,interface]=set([o2])
        try:
            self.interfaces[o1].add(interface)
        except KeyError:
            self.interfaces[o1]=set([interface])
    
    ##
    ## Lookup FIB for path.
    ## Returns interface or None, if not path found
    ##
    def lookup(self,o1,o2):
        if o1 is None:
            return [(a,o2,self.fib[a,o2]) for a,b in self.fib if b==o2]
        elif o2 is None:
            return [(o1,b,self.fib[o1,b]) for a,b in self.fib if a==o1]
        else:
            try:
                return self.fib[o1,o2]
            except KeyError:
                return None
    
    ##
    ##
    ##
    def lookup2(self,o,o1,o2):
        i1=self.lookup(o,o1)
        if i1:
            i2=self.lookup(o,o2)
            if i2:
                return (i1,i2)
        return (None,None)
    
    ##
    ## Interface visibility lookup
    ##
    def ilookup(self,o,i):
        try:
            return self.ifib[o,i]
        except KeyError:
            return set()
    
    ##
    def size(self):
        return len(self.fib)
    size=property(size)
    
    ##
    def report(self,label=None):
        n=len(self.interfaces.keys())
        s=self.size
        ms=n*(n-1)
        if label:
            print "==== %s ===="%label
        if not s:
            print "FIB: Empty"
            return
        if ms:
            print "FIB size",s,"of",ms,"(%5.2f%%)"%(float(s*100)/float(ms))
        n_interfaces=0
        for i in self.interfaces.values():
            n_interfaces+=len(i)
        print "    Topology interfaces:",n_interfaces,"of",2*len(self.interfaces)-2
    
    #
    def dump_csv(self):
        import csv
        with open("/tmp/topo-fib.csv","w") as f:
            objects=sorted(self.interfaces,lambda x,y:cmp(x.name,y.name))
            w=csv.writer(f)
            w.writerow([""]+objects+["Interfaces"])
            for o1 in objects:
                row=[o1]
                interfaces=set()
                for o2 in objects:
                    if o1==o2:
                        row+=["-"]
                    else:
                        i=self.lookup(o1,o2)
                        if i:
                            row+=[i]
                            interfaces.add(i)
                        else:
                            row+=["???"]
                row+=[",".join(sorted(interfaces))]
                w.writerow(row)
        
    #
    def between(self,o,o1,o2):
        i1=self.lookup(o,o1)
        if i1:
            i2=self.lookup(o,o2)
            if i2:
                return i1!=i2
        return False
    #
    def get_incomplete_paths(self):
        for o1 in self.interfaces:
            for o2 in self.interfaces:
                if o1!=o2 and (o1,o2) not in self.fib:
                    yield o1,o2
    #
    def classify_objects(self):
        self.objects=set(self.interfaces)
        self.leaves=set([o for o in self.objects if len(self.interfaces[o])==1])
        self.branches=self.objects-self.leaves
    

##
## MAC-adress-based discovery
##
class MACTopology(Topology):
    def __init__(self,data,hints=[],per_vlan=None):
        self.per_vlan=per_vlan
        self.interface_macs=Counter() # (object,interface)-> mac count
        self.interface_vlans={}       # (object,interface)->set of vlans
        self.mac_interfaces={}        # mac_label -> [(object,interface)]
        self.object_macs={}
        self.fib=FIB()                
        self.data=data
        super(MACTopology,self).__init__(data,hints)
    
    ##
    ## Process ARP Cache
    ##
    def process_arp_cache(self):
        object_addresses=dict([(o.address,o) for o,d in self.data])
        for o,d in self.data:
            if not d["has_mac"] or not d["has_arp"]:
                continue
            mac_interface={} # MAC -> interface
            for r in d["mac"]:
                mac_interface[r["mac"]]=r["interfaces"][0]
            for r in d["arp"]:
                ip=r["ip"]
                mac=r["mac"]
                if ip in object_addresses:
                    ro=object_addresses[ip]
                    if mac not in self.object_macs:
                        # Set up object_macs
                        self.object_macs[mac]=ro
                    # Resolve ARP interface via MAC database
                    # (Some swithces report SVI in ARP, instead of port)
                    if mac in mac_interface:
                        # Install to FIB
                        self.fib.add(o,ro,mac_interface[mac])
    
    ##
    ## Process MAC Database
    ##
    def process_mac_interfaces(self):
        for o,d in self.data:
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
                interface=r["interfaces"][0]
                mac_label="[%d]%s"%(vlan_id,mac)
                # Update interface macs count
                self.interface_macs.update((o,interface))
                # Update mac_interfaces
                try:
                    self.mac_interfaces[mac_label]+=[(o,interface)]
                except KeyError:
                    self.mac_interfaces[mac_label]=[(o,interface)]
                # Update interface vlans
                try:
                    self.interface_vlans[o,interface].add(vlan_id)
                except KeyError:
                    self.interface_vlans[o,interface]=set([vlan_id])
    ##
    ## Return unique MAC groups
    ##
    def get_unique_mac_interfaces(self):
        seen=set()
        mac_interfaces=[]
        g=0
        for m,I in self.mac_interfaces.items():
            if len(I)==1:
                # Skip MAC if seen only at single interface, since no topology knowledge within
                continue
            I=tuple(I)
            if I not in seen:
                mac_interfaces+=[(g,I)]
                g+=1
                seen.add(I)
        return mac_interfaces
    ##
    ## Detect access interfaces and populate FIB
    ##
    def process_access_interfaces(self,mac_interfaces):
        processed=set()
        for m,I in mac_interfaces:
            one=set()
            many=set()
            one_vlan=set()
            many_vlans=set()
            for o,i in I:
                if self.interface_macs[o,i]==1:
                    one.add((o,i))
                else:
                    many.add((o,i))
                if len(self.interface_vlans[o,i])==1:
                    one_vlan.add((o,i))
                else:
                    many_vlans.add((o,i))
            if len(one)==1 and len(many)>0:
                o2,i2=list(one)[0]
                for o,i in many:
                    self.fib.add(o,o2,i)
                processed.add(m)
            elif len(one_vlan)==1 and len(many_vlans)>0 and False:
                o2,i2=list(one_vlan)[0]
                for o,i in many_vlans:
                    self.fib.add(o,o2,i)
                processed.add(m)
        return [(m,I) for m,I in mac_interfaces if m not in processed]
    
    ##
    ## Remove MAC groups that contained within other groups
    ##
    def merge_macs(self,mac_interfaces):
        im={}
        mi={}
        processed=set()
        for m,I in mac_interfaces:
            for o,i in I:
                try:
                    im[o,i].add(m)
                except KeyError:
                    im[o,i]=set([m])
                try:
                    mi[m].add((o,i))
                except KeyError:
                    mi[m]=set([(o,i)])
        # Try to merge
        for m,I in mac_interfaces:
            s=mi[m]
            # Check superset candidates
            for mm in reduce(lambda x,y:x&y, [im[o,i] for o,i in I]):
                if m==mm:
                    continue
                ss=mi[mm]
                if s.issubset(ss):
                    processed.add(m)
                    break
        return [(m,I) for m,I in mac_interfaces if m not in processed]
    ##
    ## Detect interfaces leading outside the topology
    ##
    def process_egress_interfaces(self,mac_interfaces):
        im={}
        mi={}
        processed=set()
        for m,I in mac_interfaces:
            for o,i in I:
                try:
                    im[o,i].add(m)
                except KeyError:
                    im[o,i]=set([m])
                try:
                    mi[m].add((o,i))
                except KeyError:
                    mi[m]=set([(o,i)])
        for m,I in mac_interfaces:
            one=set()
            many=set()
            for o,i in I:
                if len(im[o,i])==1:
                    one.add((o,i))
                else:
                    many.add((o,i))
            if len(one)==1 and len(many)>0:
                o2=list(one)[0][0]
                for o,i in many:
                    self.fib.add(o,o2,i)
                processed.add(m)
        return [(m,I) for m,I in mac_interfaces if m not in processed]
    
    ##
    ## Populate FIB with records directly leading from existing ones
    ##
    def refine_fib(self):
        for o1 in self.fib.interfaces:
            for o2 in self.fib.interfaces:
                if o1==o2 or self.fib.lookup(o1,o2):
                    continue
                for o3 in self.fib.interfaces:
                    if o3==o1 or o3==o2:
                        continue
                    i13=self.fib.lookup(o1,o3)
                    if i13:
                        i31=self.fib.lookup(o3,o1)
                        if i31:
                            i32=self.fib.lookup(o3,o2)
                            if i32 and i31!=i32:
                                self.fib.add(o1,o2,i13)
                                break
    
    ##
    ## Prepare FIB and reverse FIB
    ##
    def build_fib(self):
        self.process_arp_cache()
        self.fib.report("ARP Cache")
        self.process_mac_interfaces()
        mac_interfaces=self.get_unique_mac_interfaces()
        mac_interfaces=self.merge_macs(mac_interfaces)
        mac_interfaces=self.process_egress_interfaces(mac_interfaces)
        self.fib.report("Egress interfaces")
        self.refine_fib()
        self.fib.report("Refine FIB")
        self.fib.classify_objects()
        if True:
            print "Unprocessed entries: ",len(mac_interfaces)
            for m,I in mac_interfaces:
                print str(m)+":"
                for o,i in I:
                    print "    ","(+)" if self.fib.ilookup(o,i) else "(-)",o,i
            print "INTERFACES"
            interfaces={}
            for I in self.mac_interfaces.values():
                for o,i in I:
                    try:
                        interfaces[o].add(i)
                    except KeyError:
                        interfaces[o]=set([i])
            for o in interfaces:
                print o,":"
                print "       Interface |FIB| MACS | VLANS"
                for i in sorted(interfaces[o]):
                    print "    %12s | %s | %04d | %04d"%(i,"+" if self.fib.ilookup(o,i) else ("?" if len(self.interface_vlans[o,i])>1 else "-"),self.interface_macs[o,i],len(self.interface_vlans[o,i]))
    
    ##
    ## Generate links using FIB
    ##
    def get_links(self):
        objects=set(self.fib.interfaces)
        if len(objects)<2:
            raise StopIteration
        candidates=[]
        for o1,o2 in combinations(objects,2):
            i1=self.fib.lookup(o1,o2)
            if i1:
                i2=self.fib.lookup(o2,o1)
                if i2:
                    if self.fib.ilookup(o1,i1)&self.fib.ilookup(o2,i2):
                        continue
                    between=[o for o in objects-set([o1,o2]) if self.fib.between(o,o1,o2)]
                    if not between:
                        candidates+=[(o1,i1,o2,i2)]
        for o1,i1,o2,i2 in candidates:
            yield o1,i1,o2,i2
        
    ## Discovery process.
    ## Generator returning resolved links
    ##
    def discover(self):
        self.build_fib()
        self.fib.report("Build FIB")
        self.fib.dump_csv()
        #
        for l in self.get_links():
            yield l
        print "DONE"
