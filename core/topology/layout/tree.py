# ----------------------------------------------------------------------
# Tree layout class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import math

# Third-party modules
import networkx as nx
import numpy as np

# NOC modules
from noc.config import config
from .base import LayoutBase


class TreeLayout(LayoutBase):
    # Horizontal step
    TREE_DX = config.layout.tree_horizontal_step
    # Vertical step
    TREE_DY = config.layout.tree_vertical_step
    CHILDREN_PER_LEVEL = 10.0
    MAX_LEVELS = config.layout.tree_max_levels

    def get_layout(self):
        G = self.topology.G
        top = self.topology.get_uplinks()
        if not top:
            # No uplinks, detect roots of trees
            top = []
            # For all connected clusters
            for cc in nx.connected_components(G):
                # Detect fattest node
                top += [
                    sorted(
                        cc, key=lambda x: G.nodes[x].get("level", self.DEFAULT_LEVEL), reverse=True
                    )[0]
                ]
        # Calculate tree width
        w = sum(self.get_tree_width(G, n) for n in top)
        # Assign positions
        x0 = 0
        pos = {}
        for u in top:
            pos.update(self.get_tree_pos(G, u, x0, w))
            x0 += G.nodes[u]["tree_width"]
        check = {x[1] for x in pos.values()}
        if len(check) == 1:
            # If all y coordinates is same, mark nodes as isolated
            return {}
        return pos

    @staticmethod
    def get_tree_width(G, node, uplink=None):
        """
        Calculate children tree width (in columns)
        :param G: Graph instance
        :param node: Tree root
        :param uplink: Exclude uplink direction for recursive descent
        :returns: Tree width
        """
        downlinks = [n for n in nx.all_neighbors(G, node) if n != uplink]
        w = 0
        for d in downlinks:
            w += TreeLayout.get_tree_width(G, d, node)
        w = max(w, 1)
        G.nodes[node]["tree_width"] = w
        G.nodes[node]["tree_downlinks"] = downlinks
        return w

    @classmethod
    def get_tree_pos(cls, G, node, x0=0, total_w=0, level=0, offset=0.0):
        """
        Calculate tree nodes positions.
        Tree must be precalculated with get_tree_width function
        :param G: Graph instance
        :param node: root node
        :param x0: x coordinate offset
        :param total_w: total tree width
        :param level: current level
        :return: dict of node -> np.array
        """
        root = G.nodes[node]
        downlinks = root["tree_downlinks"]
        total_w = total_w or root["tree_width"]
        x = x0 + root["tree_width"] // 2
        if downlinks and root["tree_width"] % 2 == 0 and x > total_w // 2:
            x -= 1
        pos = {node: np.array([x * cls.TREE_DX + offset, level * cls.TREE_DY])}
        dl = min(math.ceil(root["tree_width"] / cls.CHILDREN_PER_LEVEL), cls.MAX_LEVELS)
        for d in downlinks:
            pos.update(cls.get_tree_pos(G, d, x0, total_w, level + dl, offset))
            x0 += G.nodes[d]["tree_width"]
        return pos
