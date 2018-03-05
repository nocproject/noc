# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Ring layout class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import math
# Third-party modules
import networkx as nx
import numpy as np
# NOC modules
from .tree import TreeLayout


class RingLayout(TreeLayout):
    # Ring edge length
    L = 150
    # Chain edge step
    LL = 120
    # Spacing between parallel chains
    S = 100
    # Position of first node
    A0 = - math.pi / 2.0

    def get_layout(self):
        T = self.topology
        G = T.G
        uplinks = T.get_uplinks()
        ring = T.get_rings()[0]
        # Try to start ring with uplink
        for u in uplinks:
            if u in ring:
                i = ring.index(u)
                ring = ring[i:] + ring[:i]
                break
        # Set ring direction according to uplink's interfaces
        if len(uplinks) == 1:
            o = T.order_nodes(ring[0], [ring[1], ring[-1]])
            if o[0] != ring[1]:
                # Reverse ring
                ring = [ring[0]] + list(reversed(ring[1:]))
        # Split to subtrees
        # and calculate relative positions
        subtree_pos = self.get_subtrees_relative_pos(G, ring)
        #
        pos = {}
        # Ring length
        N = len(ring)
        # Ring radius
        R = float(N) * self.L / (2.0 * math.pi)
        # @todo: get first node
        # Angle between ring nodes
        alpha = 2.0 * math.pi / N
        # Offset angle from X-axis
        a0 = self.A0
        # Initial position considers (0, 0) is the center of ring
        # All nodes will be transformed later when we will know
        # final size of graph
        # Position nodes counterclockwise
        for i, o in enumerate(ring):
            # Node angle
            a = a0 + alpha * i
            # Ring member coordinates
            xi = R * math.cos(a)
            yi = R * math.sin(a)
            # Set ring member position
            pos[o] = np.array([xi, yi])
            # Apply affine transformation to related subtree
            st_pos = subtree_pos.get(o)
            if not st_pos or len(st_pos) == 1:
                continue  # No subtree
            # Convert calculated related coordinates
            # to absolute ones.
            # Tree is growing downwards, so subtract pi/2 from angle
            ea = a - math.pi / 2.0
            # Rotation matrix
            AA = np.array([
                [math.cos(ea), -math.sin(ea)],
                [math.sin(ea), math.cos(ea)]
            ])
            for oo in st_pos:
                if o == oo:
                    continue  # Already placed
                # Affine transformation
                # Rotate using rotation matrix
                # and shift to center of root node
                pos[oo] = np.dot(AA, st_pos[oo]) + pos[o]
        return pos

    @classmethod
    def get_subtrees_relative_pos(cls, G, ring):
        """
        Split subgraph with tree, starting from ring node
        :param G: Graph instance
        :param ring: all ring nodes
        :return: dict or ring node -> dict of positions
        """
        r = {}
        # Ring members set
        ring_set = set(ring)
        # Partition by ring
        # Remove all ring edges, splitting graph to series
        # of trees
        GG = G.subgraph(G)
        for u, v in zip(ring, ring[1:] + [ring[0]]):
            GG.remove_edge(u, v)
        # Get all remaining connected components
        for subtree in nx.connected_components(GG):
            root = subtree & ring_set
            if not root:
                continue  # Not connected to ring
            root = root.pop()
            # Get subgraph containing subtree with root
            ST = GG.subgraph(subtree)
            # Apply tree widths and arrange to levels
            w = cls.get_tree_width(ST, root)
            # Calculate relative offset
            offset = -(w // 2) * cls.TREE_DX
            # Calculate relative positions for subtree
            r[root] = cls.get_tree_pos(ST, root, offset=offset)
        return r
