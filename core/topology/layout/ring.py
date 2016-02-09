# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Ring layout class
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import math
from collections import defaultdict
## Third-party modules
import networkx as nx
import numpy as np
## NOC modules
from base import LayoutBase


class RingLayout(LayoutBase):
    # Ring edge length
    L = 150
    # Chain edge step
    LL = 120
    # Spacing between parallel chains
    S = 100
    # Position of first node
    A0 = math.pi / 2.0

    def get_layout(self):
        T = self.topology
        # unconnected = set(T.get_unconnected())
        uplinks = T.get_uplinks()
        ring = T.get_rings()[0]
        pos = {}
        # Ring length
        N = len(ring)
        # Ring radius
        R = float(N) * self.L / (2.0 * math.pi)
        # @todo: get first node
        # Angle beetween ring nodes
        alpha = 2.0 * math.pi / N
        # Offset angle from X-axis
        a0 = self.A0
        # Initial position considers (0, 0) is the center of ring
        # All nodes will be transformed later when we will know
        # final size of graph

        chains = self.get_chains()
        # Position nodes counterclockwise
        for i, o in enumerate(ring):
            # Node angle
            a = a0 + alpha * i
            xi = R * math.cos(a)
            yi = R * math.sin(a)
            pos[o] = np.array([xi, yi])
            # Place related chains
            # Calculate in relative coordinates
            # Where (0, 0) is a center of appropriative ring node
            # Rotation matrix
            AA = np.array([
                [math.cos(a), -math.sin(a)],
                [math.sin(a), math.cos(a)]
            ])
            n = len(chains[o])
            for j, chain in enumerate(chains[o]):
                for k, oo in enumerate(chain):
                    xx = np.array([
                        (k + 1) * self.LL,
                        self.S * (float(n - 1) / 2 - j)
                    ])
                    # Affine transformation.
                    # Shift to center of main node and rotate to *a*
                    pos[oo] = np.dot(AA, xx) + pos[o]
        return pos

    def get_chains(self):
        """
        Returns all direct chains
        main -> [[chain1, ...], ..., [chainN, ...]]
        """
        r = defaultdict(list)
        ring = self.topology.get_rings()[0]
        sring = set(ring)
        G = self.topology.G
        # Partition by ring
        GG = G.subgraph(G)
        for u, v in zip(ring, ring[1:] + [ring[0]]):
            GG.remove_edge(u, v)
        # Get all remaining connected components
        for chains in nx.connected_components(GG):
            main = chains & sring
            if not main:
                continue
            main = main.pop()
            # Split to particular chains
            GGG = GG.subgraph([o for o in chains if o != main])
            seen = set()
            for chain in nx.connected_components(GGG):
                ch = "-".join(str(hh) for hh in sorted(chain))
                if ch in seen:
                    continue
                else:
                    seen.add(ch)
                # Order chain
                cdata = []
                p = main
                while chain:
                    neighbors = set(nx.all_neighbors(GG, p))
                    p = (neighbors & chain).pop()
                    cdata += [p]
                    chain.remove(p)
                r[main] += [cdata]
        return r
