# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
#  Tree layout class
# ----------------------------------------------------------------------
#  Copyright (C) 2007-2018 The NOC Project
#  See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import math
# Third-party modules
import networkx as nx
import numpy as np
# NOC modules
from .base import LayoutBase


class TreeLayout(LayoutBase):
    # Horizontal step
    DX = 100
    # Vertical step
    DY = 100
    #
    CHILDREN_PER_LEVEL = 10.0
    MAX_LEVELS = 4

    def get_layout(self):
        T = self.topology
        top = T.get_uplinks()
        if not top:
            # No uplinks, detect roots of trees
            top = []
            # For all connected clusters
            for cc in nx.connected_components(T.G):
                # Detect fattest node
                top += [
                    sorted(
                        cc,
                        key=lambda x: T.G.node[x]["level"],
                        reverse=True
                    )[0]
                ]
        # Calculate tree width
        w = sum(self.get_width(n) for n in top)
        # Assign positions
        x0 = 0
        pos = {}
        for u in top:
            pos.update(self.get_pos(u, x0, w))
            x0 += T.G.node[u]["tree_width"]
        return pos

    def get_width(self, node, uplink=None):
        """
        Calculate children tree width
        """
        T = self.topology
        downlinks = list(n for n in nx.all_neighbors(T.G, node) if n != uplink)
        w = 0
        for d in downlinks:
            w += self.get_width(d, node)
        w = max(w, 1)
        T.G.node[node]["tree_width"] = w
        T.G.node[node]["tree_downlinks"] = downlinks
        return w

    def get_pos(self, node, x0, total_w, level=0):
        T = self.topology
        n = T.G.node[node]
        downlinks = n["tree_downlinks"]
        x = x0 + n["tree_width"] // 2
        if downlinks and n["tree_width"] % 2 == 0 and x > total_w // 2:
            x -= 1
        pos = {
            node: np.array([
                x * self.DX,
                level * self.DY
            ])
        }
        dl = min(math.ceil(n["tree_width"] / self.CHILDREN_PER_LEVEL), self.MAX_LEVELS)
        for d in downlinks:
            pos.update(
                self.get_pos(d, x0, total_w, level + dl)
            )
            x0 += T.G.node[d]["tree_width"]
        return pos
