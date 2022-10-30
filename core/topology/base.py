# ----------------------------------------------------------------------
# BaseMapTopology class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
from typing import Optional, List, Set, Dict, Any
from dataclasses import asdict

# Third-Party modules
import networkx as nx
import numpy as np
import cachetools

# NOC modules
from noc.core.stencil import stencil_registry, Stencil
from noc.core.text import alnum_key
from .layout.ring import RingLayout
from .layout.spring import SpringLayout
from .layout.tree import TreeLayout
from .types import ShapeOverlay


class TopologyBase(object):
    """
    Base Class for Map generators. Loaded by name
    """

    name: str  # Map Generator Name
    version: int = 0  # Generator version

    CAPS: Set[str] = {"Network | STP"}
    # Top padding for isolated nodes
    ISOLATED_PADDING = 50
    # Minimum width to place isolated nodes
    ISOLATED_WIDTH = 300
    # Row height of isolated nodes
    ISOLATED_ROW_HEIGHT = 50
    # Horizontal step for isolated nodes
    ISOLATED_STEP = 100
    # Maximum spacing between aggregated links
    AGG_LINK_SPACING = 10
    # Fixed map shifting
    MAP_OFFSET = np.array([50, 20])

    def __init__(
        self,
        gen_id: str,
        node_hints: Optional[Dict[str, Any]] = None,
        link_hints: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        self.gen_id = gen_id
        #
        self.node_hints = node_hints or {}
        self.link_hints = link_hints or {}
        self.default_stencil = stencil_registry.get(stencil_registry.DEFAULT_STENCIL)
        # Caches
        self._rings_cache = {}
        self._isolated_cache = {}
        # Graph
        self.G = nx.Graph()
        self.caps: Set[str] = set()
        self.options = kwargs
        self.load()  # Load nodes

    def __len__(self):
        """
        Map nodel count
        :return:
        """
        return len(self.G)

    def __contains__(self, item):
        return item.id in self.G

    @property
    def title(self):
        return f"{self.gen_id}"

    def load(self):
        """
        Load objects and links by  id
        """
        ...

    def add_node(self, o: Any, n_type: str, attrs: Optional[Dict[str, Any]] = None) -> None:
        """
        Add node to map
        :param o: Object
        :param n_type: Node type
        :param attrs: Additional attributes
        :return:
        """
        attrs = attrs or {}
        o_id = str(o.id)
        if o_id in self.G.nodes:
            # Only update attributes
            self.G.nodes[o_id].update(attrs)
            return
        stencil = self.get_node_stencil(o)
        # Get capabilities
        oc = set()
        if hasattr(o, "get_caps"):
            oc = set(o.get_caps()) & self.CAPS
            self.caps |= oc
        # Apply node hints
        attrs.update(self.node_hints.get(o_id) or {})
        # Apply default attributes
        attrs.update(
            {
                "mo": o,
                "type": n_type,
                "id": o_id,
                "name": o.name,
                "shape": getattr(stencil, "path", ""),
                "shape_width": getattr(stencil, "width", 0),
                "shape_height": getattr(stencil, "height", 0),
                "shape_overlay": [asdict(x) for x in self.get_node_stencil_overlays(o)],
                "ports": [],
                "caps": list(oc),
            }
        )
        self.G.add_node(o_id, **attrs)

    def add_link(self, o1: str, o2: str, attrs: Optional[Dict[str, Any]] = None):
        """
        Add link between interfaces to topology
        """
        a = {"connector": "normal"}
        if attrs:
            a.update(attrs)
        a.update({"type": "link"})
        #
        self.G.add_edge(o1, o2, **a)

    def get_node_stencil(self, o: Any) -> Optional[Stencil]:
        """
        Return node stencil
        :param o:
        :return:
        """
        return self.default_stencil

    @staticmethod
    def get_node_stencil_overlays(o: Any) -> List[ShapeOverlay]:
        """
        Return node Stencil Overlays
        :param o: Object
        :return:
        """
        return []

    def order_nodes(self, uplink, downlinks):
        """
        Sort downlinks basing on uplink's interface
        :param uplink: managed object id
        :param downlinks: ids of downlinks
        :returns: sorted list of downlinks
        """
        id_to_name = {}
        dl_map = {}  # downlink -> uplink port
        for p in self.G.nodes[uplink]["ports"]:
            id_to_name[p["id"]] = sorted(p["ports"], key=alnum_key)[0]
        for dl in downlinks:
            for p in self.G.edges[uplink, dl]["ports"]:
                if p in id_to_name:
                    dl_map[dl] = id_to_name[p]
                    break
        return sorted(dl_map, key=lambda x: alnum_key(dl_map[x]))

    @cachetools.cachedmethod(operator.attrgetter("_rings_cache"))
    def get_rings(self):
        """
        Return list of all rings
        """
        return list(nx.cycle_basis(self.G))

    @cachetools.cachedmethod(operator.attrgetter("_isolated_cache"))
    def get_isolated(self):
        """
        Returns list of nodes without connections
        """
        return list(nx.isolates(self.G))

    def non_isolated_graph(self):
        isolated = set(self.get_isolated())
        return self.G.subgraph([o for o in self.G.nodes if o not in isolated])

    def normalize_pos(self, pos):
        """
        Normalize positions, shift to (0, 0).
        Returns width, height, post
        """
        maxv = np.array([0, 0])
        minv = np.array([0, 0])
        for p in pos.values():
            maxv = np.maximum(maxv, p)
            minv = np.minimum(minv, p)
        # Dimensions
        s = maxv - minv
        # Shift positions according to offset and node size
        for p in pos:
            so = np.array(
                [self.G.nodes[p]["shape_width"] / 2.0, self.G.nodes[p]["shape_height"] / 2.0]
            )
            pos[p] -= minv + so - self.MAP_OFFSET
        return s[0], s[1], pos

    def get_layout_class(self):
        if not len(self.G):
            # Empty graph
            return SpringLayout
        if "force_spring" not in self.options and len(self.get_rings()) == 1:
            return RingLayout
        elif "force_spring" not in self.options and nx.is_forest(self.G):
            return TreeLayout
        else:
            return SpringLayout

    def layout(self):
        """
        Fill node coordinates
        :return:
        """
        # Use node hints
        dpos = {}
        for p, nh in self.node_hints.items():
            if "x" in nh and "y" in nh:
                dpos[p] = np.array([nh["x"], nh["y"]])
        if len(dpos) != len(self.G) and len(self.G):
            # Build layout
            pos = self.get_layout_class()(self).get_layout()
            pos.update(dpos)
        else:
            pos = dpos
        pos = {o: pos[o] for o in pos if o in self.G.nodes}
        width, height, pos = self.normalize_pos(pos)
        # Place isolated nodes
        isolated = sorted(
            (o for o in self.G if o not in pos), key=lambda x: self.G.nodes[x]["name"]
        )
        y = height + self.ISOLATED_PADDING
        x = 0
        w = max(width, self.ISOLATED_WIDTH)
        for i, o in enumerate(isolated):
            pos[o] = np.array([x, y + self.ISOLATED_ROW_HEIGHT * (i % 2)])
            x += self.ISOLATED_STEP
            if x > w:
                x = 0
                y += self.ISOLATED_ROW_HEIGHT * 2
        # Write positions to object's properties
        for o in pos:
            x, y = pos[o]
            self.G.nodes[o]["x"] = x
            self.G.nodes[o]["y"] = y
        # Calculate link positions
        for u, v in self.G.edges():
            ed = self.G[u][v]
            if ed["id"] in self.link_hints:
                # Use existing hints
                ed.update(self.link_hints)
            # @todo: Calculate new positions
