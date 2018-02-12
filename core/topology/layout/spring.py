# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Spring layout class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import math
# Third-party modules
import networkx as nx
# NOC modules
from .base import LayoutBase


class SpringLayout(LayoutBase):
    SCALE_FACTOR = 130
    # Average distance between nodes
    L = 150

    def get_layout(self):
        G = self.topology.non_isolated_graph()
        # Adjust weights
        for e in G.edges_iter():
            o1, o2 = e[0], e[1]
            G.edge[o1][o2]["weight"] = self.get_weight(
                G.node[o1].get("level", self.DEFAULT_LEVEL),
                G.node[o2].get("level", self.DEFAULT_LEVEL),
            )
        #
        scale = self.SCALE_FACTOR * math.sqrt(len(G))
        k = self.L / scale
        return nx.spring_layout(
            G,
            scale=scale,
            k=k,
            iterations=100
        )

    @classmethod
    def get_weight(cls, l1, l2):
        return 2 * cls.DEFAULT_LEVEL * (l1 + l2) / cls.L
