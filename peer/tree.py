# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Prefix-list-optimizing tree
##
## Tree is a binary tree containing prefixes.
## Each prefix is represented as sequence of the bits.
## All prefixes start with root.
## Zero bit on apropriative position in prefix means
## the prefix will be directed left from current node.
## The set bit means right direction.
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.lib.ip import prefix_to_bin,bin_to_prefix

class Node(object):
    def __init__(self,parent=None,prefix=[]):
        self.parent=parent
        self.prefix=prefix
        self.children=[None,None]
        self.is_final=False
        
    # Binary prefix is a list of integers
    def append_binary_prefix(self,prefix):
        if not prefix:
            # Optimization #1
            # Remove existing specifics
            # When summary accepted
            if not self.is_final:
                self.release_children()
            # Mark this node as final
            self.is_final=True
            return
        # Optimization #2
        # Do not append specifics when summary exists
        if self.is_final:
            return
        d=prefix.pop(0)
        # Optimization #3
        # Do not append child when another final child exists.
        # Make this node final instead (summarize two prefixes)
        if not prefix:
            c=[c for c in self.children if c is not None]
            if len(c):
                if c[0].is_final:
                    self.release_children()
                    # Optimization #4
                    # When summarized prefixes try to summarize
                    # with siblings
                    n=self.parent
                    while n:
                        if len([c for c in n.children if c and c.is_final])==2:
                            n.release_children()
                            n=n.parent
                        else:
                            break
                    return
        # Cannot reduce prefix (yet). Append to the tree
        if not self.children[d]:
            self.children[d]=Node(self,self.prefix+[d])
        self.children[d].append_binary_prefix(prefix)
        
    def append_prefix(self,prefix):
        self.append_binary_prefix(prefix_to_bin(prefix))
        
    #
    # Extract remaining prefixes into list r
    #
    def extract_prefixes(self,r):
        if self.is_final:
            r.append(bin_to_prefix(self.prefix))
        [c.extract_prefixes(r) for c in self.children if c is not None]
        return r
        
    def release(self):
        self.parent=None
        self.release_children()
        
    def release_children(self):
        [c.release() for c in self.children if c is not None]
        self.children=[None,None]
        self.is_final=True

def optimize_prefix_list(prefix_list):
    """
    Optimize prefix list. Prefix list is a list of prefixes.
    Returns reduced list of prefixes
    
    Check optimization #1
    >>> optimize_prefix_list(["192.168.128.0/24","192.168.0.0/16"])
    ['192.168.0.0/16']
    Check optimization #2
    >>> optimize_prefix_list(["192.168.0.0/16","192.168.128.0/24"])
    ['192.168.0.0/16']
    Check optimization #3
    >>> optimize_prefix_list(["192.168.0.0/24","192.168.1.0/24"])
    ['192.168.0.0/23']
    Check optimization #4
    >>> optimize_prefix_list(["192.168.0.0/24","192.168.1.0/24","192.168.2.0/24","192.168.3.0/24"])
    ['192.168.0.0/22']
    >>> optimize_prefix_list(["192.168.%d.0/24"%i for i in range(16)])
    ['192.168.0.0/20']
     >>> optimize_prefix_list(["192.168.%d.0/24"%i for i in range(17)])
    ['192.168.0.0/20', '192.168.16.0/24']
    """
    n=Node()
    for p in prefix_list:
        n.append_prefix(p)
    r=[]
    n.extract_prefixes(r)
    return r
