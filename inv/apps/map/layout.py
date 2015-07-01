# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Segment Layout engine
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import math
from collections import defaultdict
## Third-party modules
import networkx as nx


class Layout(object):
    SCALE_FACTOR = 130
    LINK_SPACING = 10

    def __init__(self):
        self.G = nx.Graph()
        self.seen_links = {}  # n1, n2 -> count
        self.link_ids = defaultdict(list)  # n1, n2 -> [link id]
        self.node_size = {}  # n -> w, h
        self.fixed_positions = {}  # n -> x, y
        self.width = None
        self.height = None

    def add_link(self, n1, n2, lid):
        if n1 == n2:
            return
        lp = (min(n1, n2), max(n1, n2))
        self.link_ids[lp] += [lid]
        if len(self.link_ids[lp]) > 1:
            return
        self.G.add_edge(lp[0], lp[1])

    def set_node_size(self, n, w, h):
        self.node_size[n] = (w, h)

    def set_node_position(self, n, x, y):
        self.fixed_positions[n] = (x, y)

    def set_page_size(self, w, h):
        self.width = w
        self.height = h

    def layout(self):
        """
        Auto-layout graph
        Retuns dict of nodes positions, dict of links hints
        """
        if len(self.fixed_positions) == len(self.G):
            npos = self.fixed_positions
        else:
            npos = self.layout_spring()
        # Set link hints
        lpos = {}
        for l in self.link_ids:
            c = len(self.link_ids[l])
            if c == 1:
                continue
            # Calculate link hints
            m0, m1 = l
            x0, y0 = npos[m0]
            x1, y1 = npos[m1]
            # Adjust to node sizes
            w0, h0 = self.node_size[m0]
            x0 += w0 / 2
            y0 += h0 / 2
            w1, h1 = self.node_size[m1]
            x1 += w1 / 2
            y1 += h1 / 2
            # Calculte sin and cos
            L = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
            sin_a = (y1 - y0) / L
            cos_a = (x1 - x0) / L
            w = float(self.LINK_SPACING * (c - 1))  # Span width
            xc = (x0 + x1) / 2  # Center of segment
            yc = (y0 + y1) / 2
            for i, lid in enumerate(self.link_ids[l]):
                k = w / 2 - i * w / (c - 1)
                xi = xc - k * sin_a
                yi = yc + k * cos_a
                lpos[lid] = [{"x": xi, "y": yi}]
        return npos, lpos

    def layout_spring(self):
        """
        Fruchterman-Reingold force-directed algorithm
        """
        if not self.width or not self.height:
            scale = self.SCALE_FACTOR * math.sqrt(len(self.G))
        else:
            scale = max(self.width, self.height)

        return nx.spring_layout(
            self.G,
            scale=scale,
            pos=self.fixed_positions or None,
            fixed=list(self.fixed_positions) or None
        )
