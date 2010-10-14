# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Topology Discovery Data Structures
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

##
## Simple incremental counter
## Returns a number of updates per key
##
class Counter(object):
    def __init__(self):
        self.data={}
    ##
    ## Return a counter value
    ##
    def __getitem__(self,key):
        try:
            return self.data[key]
        except KeyError:
            return 0
    ##
    ## Increment key counter per 1
    ##
    def update(self,key):
        try:
            self.data[key]+=1
        except KeyError:
            self.data[key]=1
    ##
    ## Dict items
    ##
    def items(self):
        return self.data.items()

##
## Topology node.
## A node of directed graph
## With outgoing connections edge
## And ingoing connected edges
##
class Node(object):
    dot_shape="box"
    def __init__(self,topology,name):
        self.topology=topology
        self.name=name
        self.topology.objects[self.name]=self # Register object within topology
        self.connections=set()                # A pairs of (remote_node,local_interface)
        self.connected=set()                  # A pairs of (remote_node,remote_interface)
    ##
    ##
    ##
    def __repr__(self):
        return self.name
        return "<%s %s>"%(self.__class__.__name__,self.name)
    ##
    ## Debugging dump
    ##
    def dump(self):
        print "%s %s: connections=%s connected=%s"%(self.__class__.__name__,self.name,str(self.connections),str(self.connected))
    ##
    ## Connect to node
    ##
    def connect(self,node,local_interface=None):
        self.connections.add((node,local_interface))
        node.connected.add((self,local_interface))
    ##
    ## Disconnect node
    ##
    def disconnect(self,node,remote_interface=None):
        node.connections.remove((self,remote_interface))
        self.connected.remove((node,remote_interface))
    ##
    ## Reconnect to another node
    ##
    def reconnect(self,node,local_interface,new_node):
        node.disconnect(self,local_interface)
        self.connect(new_node,local_interface)
    ##
    ## Change node's name
    ##
    def rename(self,new_name):
        del self.topology.objects[self.name]
        self.name=new_name
        self.topology.objects[self.name]=self
    ##
    ## Disconnect all ingress and egress edges
    ##
    def prune(self):
        for n,i in list(self.connections):
            n.disconnect(self,i)
        for n,i in list(self.connected):
            self.disconnect(n,i)
    ##
    ## Delete node and unregister in parent topology
    ##
    def delete(self):
        self.prune()
        del self.topology.objects[self.name]
        del self
    ##
    ## Filter only Node class instances
    ##
    @classmethod
    def filter(cls,iter):
        return [x for x in iter if isinstance(x,cls)]
    ##
    ## Filter only tuples containing class instance
    ## at first place
    ##
    @classmethod
    def filter_connects(cls,iter):
        return [x for x in iter if isinstance(x[0],cls)]
    ##
    ##
    ##
    def dot(self):
        is_object=isinstance(self,Object)
        r=["\"%s\" [shape=%s];"%(self.name,self.dot_shape)]

        for n,i in self.connections:
            is_link=False
            opts=[]
            if i:
                opts+=["label=\"%s\""%i]
            if is_object and isinstance(n,Object):
                opts+=["color=red"]
                is_link=True
            if opts:
                opts=" [%s]"%",".join(opts)
            else:
                opts=""
            r+=["\"%s\" -> \"%s\"%s;"%(self.name,n.name,opts)]
        return "\n".join(r)
##
## Managed object Node
##
class Object(Node):
    dot_shape="box"
    def __init__(self,topology,managed_object):
        self.managed_object=managed_object
        super(Object,self).__init__(topology,managed_object.name) #+"\\n"+managed_object.profile_name)
    
    def interfaces(self):
        return set([i for o,i in self.connections])
##
## Basic topology class
## Containing nodes and connections
##
class Topology(object):
    ##
    ## data is a structure specific for topology
    ## hints - links resolved during previous runs
    ##         [ ((node,interface),(node,interface)) ]
    ##
    def __init__(self,data,hints=[]):
        self.objects={}
        self.create_nodes(data,hints)
    ##
    ## Populate topology with nodes
    ##
    def create_nodes(self,data,hints):
        pass
    ##
    ## Reduce topology and detect links
    ## [(node,interface),(node,interface)]
    ##
    def discover(self):
        return []
    ##
    ## Return a list of all Object instances
    ##
    def all_objects(self):
        return Object.filter(self.objects.values())
    ##
    ## Build GraphViz DOT
    ##
    def dot(self,path=None):
        s=["digraph {"]+[o.dot() for o in self.objects.values()]+["}"]
        s="\n".join(s)
        if path:
            path="/tmp/topo-%s.dot"%path
            f=open(path,"w")
            f.write(s)
            f.close()
        return s
