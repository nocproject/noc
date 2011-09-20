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
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# NOC modules
from noc.lib.ip import *


class Node(object):
    """
    Optimizing prefix tree.
    @todo: Merge with PrefixDB
    """
    def __init__(self, parent=None, prefix=[], n=0, prefixes=None):
        self.parent = parent
        self.prefix = prefix
        self.children = [None, None]
        self.is_final = False
        self.n = 0
        if prefixes:
            for p in prefixes:
                self.append_prefix(p)

    def append_binary_prefix(self, prefix):
        """
        Append binary prefix to a tree.
        Binary prefix is a list of integers
        """
        lp = len(prefix)
        if lp > self.n:
            self.n = lp
        if not prefix:
            # Optimization #1
            # Remove existing specifics
            # When summary accepted
            if not self.is_final:
                self.release_children()
                # Mark this node as final
                self.is_final = True
            return
        # Optimization #2
        # Do not append specifics when summary exists
        if self.is_final:
            return
        d = prefix.pop(0)
        # Optimization #3
        # Do not append child when another final child exists.
        # Make this node final instead (summarize two prefixes)
        if not prefix:
            c = self.children[(d + 1) % 2]  # Other children
            if c is not None and c.is_final:
                self.release_children()
                # Optimization #4
                # When summarized prefixes try to summarize
                # with siblings
                n = self.parent
                while n:
                    if len([c for c in n.children if c and c.is_final]) == 2:
                        n.release_children()
                        n = n.parent
                    else:
                        break
                return
        # Cannot reduce prefix (yet). Append to the tree
        if not self.children[d]:
            self.children[d] = Node(self, self.prefix + [d])
        self.children[d].append_binary_prefix(prefix)

    def append_prefix(self, prefix):
        self.append_binary_prefix(list(IP.prefix(prefix).iter_bits()))

    def get_prefixes(self):
        """
        Fetch all remaining prefixes as a list
        """
        if self.is_final:
            return [IPv4.from_bits(self.prefix).prefix]
        r = []
        for c in self.children:
            if c is not None:
                r += c.get_prefixes()
        return r

    def get_prefixes_maxlen(self):
        """
        Extract remaining prefixes as a list of (prefix, maxlen)
        """
        if self.is_final:
            return [(IPv4.from_bits(self.prefix), self.n + len(self.prefix))]
        r = []
        for c in self.children:
            if c is not None:
                r += c.get_prefixes_maxlen()
        return r

    def release(self):
        """
        Drop current node from tree
        """
        self.parent = None
        self.release_children()

    def release_children(self):
        """
        Drop all children and mark node as final
        """
        [c.release() for c in self.children if c is not None]
        self.children = [None, None]
        self.is_final = True


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

    Check duplication
    >>> optimize_prefix_list(["192.168.0.0/24", "192.168.0.0/24"])
    ['192.168.0.0/24']
    """
    return Node(prefixes=prefix_list).get_prefixes()

def optimize_prefix_list_maxlen(prefix_list):
    """
    Optimize prefix list. Prefix list is a list of prefixes.
    Returns reduced list of prefixes

    Check optimization #1
    >>> optimize_prefix_list_maxlen(["192.168.128.0/24","192.168.0.0/16"])
    [(<IPv4 192.168.0.0/16>, 24)]

    Check optimization #2
    >>> optimize_prefix_list_maxlen(["192.168.0.0/16","192.168.128.0/24"])
    [(<IPv4 192.168.0.0/16>, 24)]

    Check optimization #3
    >>> optimize_prefix_list_maxlen(["192.168.0.0/24","192.168.1.0/24"])
    [(<IPv4 192.168.0.0/23>, 24)]

    Check optimization #4
    >>> optimize_prefix_list_maxlen(["192.168.0.0/24","192.168.1.0/24","192.168.2.0/24","192.168.3.0/24"])
    [(<IPv4 192.168.0.0/22>, 24)]

    >>> optimize_prefix_list_maxlen(["192.168.%d.0/24"%i for i in range(16)])
    [(<IPv4 192.168.0.0/20>, 24)]

    >>> optimize_prefix_list_maxlen(["192.168.%d.0/24"%i for i in range(17)])
    [(<IPv4 192.168.0.0/20>, 24), (<IPv4 192.168.16.0/24>, 24)]

    Check duplication
    >>> optimize_prefix_list_maxlen(["192.168.0.0/24", "192.168.0.0/24"])
    [(<IPv4 192.168.0.0/24>, 24)]
    """
    return Node(prefixes=prefix_list).get_prefixes_maxlen()
