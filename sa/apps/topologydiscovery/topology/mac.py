# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Topology Discovery
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from base import *

##
## MAC address node
##
class MAC(Node):
    dot_shape="plaintext"
    def merge(self,node):
        name=self.name+"\\n"+node.name
        node.delete()
        self.rename(name)
    def connected_to_object(self):
        return len(self.connected)==1 and isinstance(list(self.connected)[0],Object)
##
## A set of links to be resolved into single link
##
class Cloud(Node):
    dot_shape="circle"
    ##
    ##
    ##
    def rank(self):
        return (len(self.connections),len(self.connected))
    ##
    ## Merge two nodes
    ## Add all edges from second node to first
    ##
    def merge(self,node):
        for n,i in list(node.connections): # changed during iterations
            if (n,i) not in self.connections:
                self.connect(n)
                n.disconnect(node)
        for n,i in node.connected:
            if (n,i) not in self.connected:
                n.reconnect(n,i,self)
        node.delete()
    ##
    ## Unique string containing hash of all connected nodes
    ##
    def connected_hash(self):
        return ":".join(["%s,%s"%(n.name,str(i)) for n,i in sorted(self.connected,lambda x,y: cmp(x[0],y[0]))])
    ##
    def edges_hash(self):
        h1=":".join(["%s,%s"%(n.name,str(i)) for n,i in sorted(self.connections,lambda x,y: cmp(x[0],y[0]))])
        h2=":".join(["%s,%s"%(n.name,str(i)) for n,i in sorted(self.connected,lambda x,y: cmp(x[0],y[0]))])
        return "%s|%s"%(h1,h2)

class MACTopology(Topology):
    ##
    ## data = [(managed_object, get_mac_address_table result)]
    # hints = ([object, interface, object, interface])
    ##
    def __init__(self,data,hints=[]):
        self.interface_mac_count=Counter()
        self.rules_hits=Counter()
        super(MACTopology,self).__init__(data,hints)
    ##
    ## Populate topology with nodes
    ##
    def create_nodes(self,data,hints):
        mac_db=[]
        mac_count=Counter()
        for obj,mac_data in data:
            o=Object(self,obj)
            for r in mac_data:
                vlan_id=r["vlan_id"]
                mac=r["mac"]
                interfaces=r["interfaces"]
                macs_key="%d:%s"%(vlan_id,mac)
                mac_db+=[(macs_key,o,interfaces)]
                mac_count.update(macs_key)
                for i in interfaces:
                    self.interface_mac_count.update((o,i))
        cn=1
        for macs_key,o,interfaces in mac_db:
            if mac_count[macs_key]<2:
                continue
            for i in interfaces:
                if macs_key not in self.objects:
                    # Create MAC
                    m=MAC(self,macs_key)
                    # Create cloud
                    c=Cloud(self,"Cloud #%d"%cn)
                    cn+=1
                    # Attach cloud to mac
                    c.connect(m)
                else:
                    # Find cloud
                    c=list(self.objects[macs_key].connected)[0][0]
                o.connect(c,i)
    ##
    ## When
    ##      Rank(C)=(<2,0) or Rank(C)=(0,<2)
    ## Then
    ##      delete C
    def delete_if_empty(self,c):
        if (len(c.connections)==0 and len(c.connected)<2)\
            or (len(c.connections)<2 and len(c.connected)==0):
            c.delete()
            return True
        return False
    ##
    ## Returns true if it is possible to build path
    ## passing all edges and leading to destination
    ##
    def path_exists(self,edges,destination):
        for n,i in edges:
            if (n,i) in destination.connected:
                # Node connected to destination found.
                # Calculate rest of the path
                rest=[(o,j) for o,j in edges if o!=n]
                if len(rest)==0:
                    return True
                # Node became next destination for path
                return self.path_exists(rest,n)
        return False
    ##
    ## Find edges are not in spanning tree
    ## with root "root". Returns a set of
    ## not matched edges
    ##
    def not_in_tree(self,edges,root):
        rest=edges.copy()
        current_level=set([root])
        while True:
            next_level=set()
            for o,i in list(rest):
                for c in current_level:
                    if (c,i) in o.connections:
                        next_level.add(o)
                        rest.remove((o,i))
                        break
            if not rest or not next_level:
                break
            current_level=next_level
        return rest
    ##
    ## Returns an edge at the root of tree, or None
    ##
    ##
    def root_of_tree(self,edges):
        objects=set([x[0] for x in edges])
        rest=set()
        for o,i in edges:
            found=False
            for oo,j in Object.filter_connects(o.connections):
                if oo in objects and i==j:
                    found=True
                    break
            if not found:
                rest.add((o,i))
        if len(rest)==1:
            o,i=rest.pop()
            for n,e in enumerate(edges):
                print n,e
            for n,e in enumerate(edges-set([(o,i)])):
                print n,e
            if not self.not_in_tree(edges-set([(o,i)]),o):
                return o,i
        return None
        
    ##
    ## Rule #1: (1,1) cloud is a link
    ## When
    ##      O1(i)->C
    ##      C->O2
    ##      Rank(C)==(1,1)
    ## Then
    ##      delete C
    ##      O1(i)->O2
    def reduce_cloud_rule1(self,c):
        if c.rank()==(1,1):
            o1,i=list(c.connected)[0]
            o2=list(c.connections)[0][0]
            print "#1. Connect",c,o1,i,o2
            o1.connect(o2,i)
            c.delete()
            self.rules_hits.update(1)
            return True # Stop processing cloud, deleted
        return False # Not reduced, continue processing
    ##
    ## Rule #2: Delete clouds with already resolved links
    ## Wnen
    ##      O1(i1)->C
    ##      ...
    ##      ON(iN)->C
    ##      C->OM
    ##      Rank(C)=(1,N)
    ##      not_in_tree({O1(i1),..,ON(iN)},OM) == []
    ## Then
    ##      delete C
    ##
    def reduce_cloud_rule2(self,c):
        n1,n2=c.rank()
        if n1==1 and n2>1:
            rest=self.not_in_tree(c.connected,list(c.connections)[0][0])
            if not rest:
                print "#2. Already resolved cloud deleted",c
                c.delete()
                self.rules_hits.update(2)
                return True
        return False
    ##
    ## Rule #3: Reconnect cloud with one resolved link
    ##
    def reduce_cloud_rule3(self,c):
        n1,n2=c.rank()
        if n1==1 and n2>1:
            o2=list(c.connections)[0][0]
            common=o2.connected.intersection(c.connected)
            lc=len(common)
            if lc>1 and lc==n2:
                # Full match. Claud is fully resolved
                print "#3. Delete fully resolved cloud",c
                c.delete()
                return True
        return False
    ##
    ## Rule #4.
    ## When
    ##      O1(i)->C
    ##      O2(j)->C
    ##      O2(j)->O1
    ##      Rank(C)=(0,2)
    ## Then
    ##      Delete C
    def reduce_cloud_rule4(self,c):
        if c.rank()==(0,2):
            cc=list(c.connected)
            o1,i1=cc.pop()
            o2,i2=cc.pop()
            o1c=set([x[0] for x in o1.connected])
            o2c=set([x[0] for x in o2.connected])
            if o1 in o2c or o2 in o1c:
                print "#4. Delete fully resolved cloud",c
                c.delete()
                self.rules_hits.update(4)
                return True
        return False
    ##
    ## Rule #5
    ## When
    ##      Rank(C1)=(0,N+1)
    ##      Rank(C2)=0(0,N+1)
    ##      N>1
    ##      O1(i1)->C1
    ##      ...
    ##      ON(iN)->C1
    ##      O1(i1)->C2
    ##      ...
    ##      ON(iN)->C2
    ##      M=N+1
    ##      OM(i)->C1
    ##      OM(j)->C2
    ##      i!=j
    ## Then
    ##      delete OM(i)->C2
    ##      C2->OM
    ##      delete C1
    ##
    def reduce_cloud_rule5(self,c):
        n,m=c.rank()
        lc=len(c.connected)
        if n==0 and m>2:
            for o,i in c.connected:
                for cc,j in Cloud.filter_connects(o.connections):
                    if cc!=c and cc.rank()==(0,m):
                        # Find common interfaces
                        ci=c.connected.intersection(cc.connected)
                        if lc-len(ci)==1:
                            # Detect the difference belongs to common Object
                            o1,i1=list(c.connected.difference(ci)).pop()
                            o2,i2=list(cc.connected.difference(ci)).pop()
                            if o1==o2 and i1!=i2:
                                print "#5. Partially resolved cloud refined",cc
                                self.rules_hits.update(5)
                                c.delete()
                                cc.connect(o2)
                                cc.disconnect(o2,i2)
                                return True
        return False
    ##
    ## Rule #6: Resolve tree leading to node
    ## Wnen
    ##      O1(i1)->C
    ##      ...
    ##      ON(iN)->C
    ##      C->OM
    ##      Rank(C)=(1,N)
    ##      root_of_tree({O1(i1),...,ON(iN)})=O1(i1)
    ## Then
    ##      delete C
    ##      O1(i1)->OM
    ##
    def reduce_cloud_rule6(self,c):
        n1,n2=c.rank()
        if n1==1 and n2>3:
            r=self.root_of_tree(c.connected)
            if r:
                o,i=r
                ro=list(c.connections)[0][0]
                print "#6. Resolved tree",c,"Connect",o,i,ro
                c.delete()
                self.rules_hits.update(6)
                o.connect(ro,i)
                return True
        return False
    ## 
    ## Rule #6: Delete fully resolved cloud with missed root
    ## When
    ##     O1(i1)->C
    ##     ..
    ##     ON(iN)->C
    ##     Rank(C)=(0,N)
    ##     O1(i1)->O
    ##     ..
    ##     O1(iN)->O
    ## Then
    ##     delete C
    ##
    def reduce_cloud_rule7(self,c):
        n,m=c.rank()
        if n==0 and m>1:
            root=None
            for o,i in c.connected:
                found=False
                for ro,j in Object.filter_connects(o.connections):
                    if i==j:
                        if not root:
                            root=ro
                        elif root!=ro:
                            return False # No common root
                        found=True
                        break
                if not found:
                    return False # No common root
            # All nodes leads to common roots
            print "#7. All edges leads to common root. Remove",c
            self.rules_hits.update(7)
            c.delete()
            return True
        return False
    
    ##
    ## All Clouds in topology
    ##
    def all_clouds(self):
        return Cloud.filter(self.objects.values())
    ##
    ## All MACs in topology
    ##
    def all_macs(self):
        return MAC.filter(self.objects.values())
    ##
    ## All Objects connected to other objects
    ##
    def all_linked_objects(self):
        for o in self.all_objects():
            for lo in [lo for lo,x in o.connections if isinstance(lo,Object)]:
                yield (o,lo)
    ##
    ## Detect all access interfaces and reconnect clouds
    ## Access interfaceses a thouse having only one MAC,
    ## while this MACs are available on other interfaces
    ##
    def resolve_access_interfaces(self):
        access_interfaces=set()
        # Detect access interfaces
        for I,c in self.interface_mac_count.items():
            if c==1:
                access_interfaces.add(I)
        # Reconnect clouds containing access interface
        for o in self.all_objects():
            for n,i in o.connections:
                if n.connections and (o,i) in access_interfaces:
                    m=list(n.connections)[0][0]
                    o.reconnect(n,i,m)
                    n.reconnect(m,None,o)
    ##
    ## Merge all clouds with same set of edges
    ##
    def merge_duplicated_clouds(self):
        cc={} # hash -> clouds
        for c in self.all_clouds():
            h=c.connected_hash()
            if h in cc:
                cc[h]+=[c]
            else:
                cc[h]=[c]
        for ccs in [ccs for ccs in cc.values() if len(ccs)>=2]:
            # Merge clouds
            c0=ccs.pop(0)
            for c in ccs:
                c0.merge(c)
            # Compact macs
            ml=[m for m,i in c0.connections if isinstance(m,MAC)]
            if ml:
                m0=ml.pop(0)
                while len(ml)>0:
                    m0.merge(ml.pop(0))
    ##
    ##
    ##
    def delete_duplicated_clouds(self):
        cc={}
        for c in self.all_clouds():
            h=c.edges_hash()
            if h in cc:
                cc[h]+=[c]
            else:
                cc[h]=[c]
        for ccs in [ccs for ccs in cc.values() if len(ccs)>=2]:
            c0=ccs.pop(0)
            for c in ccs:
                print "Duplicated cloud %s deleted"%c
                c.delete()
    ##
    ## Returns a list of resolved links
    ##
    def get_resolved_links(self):
        seen=set()
        links=[]
        for o in self.all_objects():
            for co,i in Object.filter_connects(o.connections):
                if co in seen:
                    continue
                for cco,j in Object.filter_connects(co.connections):
                    if cco==o:
                        links+=[(o.managed_object,i,co.managed_object,j)]
                        break
            seen.add(o)
        return links
    ##
    ##
    ##
    def resolve_unique_interfaces(self):
        changed=False
        # Find unique interface
        for o in self.all_objects():
            ifaces=Counter()
            for n,i in o.connections:
                ifaces.update(i)
            for i,n in [(i,n) for i,n in ifaces.items() if n==1]:
                for c,j in Cloud.filter_connects(o.connections):
                    if i==j:
                        print "Unique interface found, resolving",c,o,i
                        c.disconnect(o,i)
                        c.connect(o)
                        changed=True
                        break
        return changed
    ##
    ##
    ##
    def resolve_backlinks(self):
        changed=False
        for o in self.all_objects():
            connected=set([n[0] for n in Object.filter_connects(o.connected)])
            connections=set([n[0] for n in Object.filter_connects(o.connections)])
            for oo in connected-connections:
                iset=set()
                n=0
                for c,i in Cloud.filter_connects(o.connections):
                    for ooo,x in c.connections:
                        if ooo==oo:
                            n+=1
                            iset.add(i)
                if n>2 and len(iset)==1:
                    i=iset.pop()
                    "Backlink found. Connect ",o,i,oo
                    o.connect(oo,i)
                    changed=True
        return changed
    ##
    ## Perform topology discovery
    ##
    def discover(self):
        self.resolve_access_interfaces()
        self.merge_duplicated_clouds()
        ## Delete all MACs
        for m in self.all_macs():
            m.delete()
        done=False
        while not done:
            done=True
            # For each cloud
            for c in self.all_clouds():
                # Apply reduction rules
                if self.reduce_cloud_rule1(c)\
                    or self.reduce_cloud_rule2(c)\
                    or self.reduce_cloud_rule3(c)\
                    or self.reduce_cloud_rule4(c)\
                    or self.reduce_cloud_rule5(c)\
                    or self.reduce_cloud_rule6(c)\
                    or self.reduce_cloud_rule7(c):
                    done=False
            #
            changed=self.resolve_unique_interfaces()
            if done and changed:
                done=False
            changed=self.resolve_backlinks()
            if done and changed:
                done=False
            # Wipe out empty clouds
            for c in self.all_clouds():
                self.delete_if_empty(c)
            # Delete duplicated clouds
            self.delete_duplicated_clouds()
        ## Generate a list of resolved links
        print "\n".join([str(r) for r in self.summary()])
        return self.get_resolved_links()
    ##
    ## Debugging. Returns a number of resolved links
    ##
    def count_links(self):
        n_links=0
        for o in self.all_objects():
            for n,i in o.connections:
                if isinstance(n,Object):
                    n_links+=1
        return n_links
    ##
    ## Debugging, Returns summary
    ##
    def summary(self):
        cloud_ranks=Counter()
        for c in self.all_clouds():
            cloud_ranks.update(c.rank())
        return [
            ("Objects",len(list(self.all_objects()))),
            ("Clouds",len(list(self.all_clouds()))),
            ("Links",self.count_links())
        ]\
        +[("Rule #%d"%x,y) for x,y in self.rules_hits.items()]\
        +[("Cloud rank %s"%str(x),y) for x,y in cloud_ranks.items()]
