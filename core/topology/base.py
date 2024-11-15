# ----------------------------------------------------------------------
# BaseMapTopology class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
from typing import Optional, List, Set, Dict, Any, Iterable, Tuple
from collections import defaultdict
from dataclasses import asdict

# Third-Party modules
import networkx as nx
import numpy as np
import cachetools
from bson import ObjectId

# NOC modules
from noc.core.stencil import stencil_registry, Stencil
from noc.core.text import alnum_key
from .layout.ring import RingLayout
from .layout.spring import SpringLayout
from .layout.tree import TreeLayout
from .types import TopologyNode, MapMeta, MapItem, PathItem


class TopologyBase(object):
    """
    Base Class for Map generators. Loaded by name
    """

    name: str  # Map Generator Name
    version: int = 0  # Generator version
    header: Optional[str] = None

    PARAMS: Set[str] = set()  # Allowed generator params
    CAPS: Set[str] = set()

    DEFAULT_LEVEL = 10
    # Allow to normalize position when displayed
    NORMALIZE_POSITION = True
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
    MAP_OFFSET = np.array([80, 40])

    def __init__(self, **settings):
        # Hints
        self.node_hints: Optional[Dict[str, Any]] = settings.get("node_hints") or {}
        self.link_hints: Optional[Dict[str, Any]] = settings.get("link_hints") or {}
        self.default_stencil = stencil_registry.get(stencil_registry.DEFAULT_STENCIL)
        #
        self.pn = 0
        # Caches
        self._rings_cache = {}
        self._isolated_cache = {}
        self._interface_cache: Dict["ObjectId", Any] = {}
        # Graph
        self.G = nx.Graph()
        self.caps: Set[str] = set()
        self.settings = settings or {}
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
    def gen_id(self) -> Optional[str]:
        raise NotImplementedError

    @property
    def title(self):
        """
        Map Title
        :return:
        """
        return f"{self.name}"

    @property
    def meta(self) -> MapMeta:
        """
        Return Map settings
        :return:
        """
        return MapMeta(title=self.title)

    def get_uplinks(self) -> List[str]:
        """
        Return uplink node for map. Use on tree layout
        :return:
        """
        return []

    def add_node(self, n: TopologyNode, attrs: Optional[Dict[str, Any]] = None) -> None:
        """
        Add node to map
        :param n: Node
        :param attrs: Additional attributes
        :return:
        """
        attrs = attrs or {}
        o_id = str(n.id)
        attrs.update(n.attrs or {})
        if o_id in self.G.nodes:
            # Only update attributes
            self.G.nodes[o_id].update(attrs)
            return
        stencil: Stencil = stencil_registry.get(n.stencil or stencil_registry.DEFAULT_STENCIL)
        # Get capabilities
        oc = set()
        if n.get_caps():
            oc = set(n.get_caps()) & self.CAPS
            self.caps |= oc
        if n.portal:
            attrs["portal"] = asdict(n.portal)
        # Apply node hints
        attrs.update(self.node_hints.get(o_id) or {})
        # Apply default attributes
        attrs.update(
            {
                "type": n.type,
                "id": o_id,
                "node_id": n.resource_id,
                "metrics_label": "",
                "metrics_template": n.title_metric_template or "",
                "level": n.level,
                "name": n.title or "",
                "shape": getattr(stencil, "path", ""),
                "shape_width": getattr(stencil, "width", 0),
                "shape_height": getattr(stencil, "height", 0),
                "shape_overlay": [asdict(x) for x in n.overlays] if n.overlays else [],
                "ports": [],
                "caps": list(oc),
                "object_filter": n.object_filter,
            }
        )
        self.G.add_node(o_id, **attrs)

    def add_edge(
        self, o1: str, o2: str, attrs: Optional[Dict[str, Any]] = None, edge_type: str = "link"
    ):
        """
        Add link between interfaces to topology
        """
        a = {"connector": "normal"}
        if attrs:
            a.update(attrs)
        a.update({"type": edge_type})
        #
        self.G.add_edge(o1, o2, **a)

    def add_link(self, link):
        """
        Add Link to Graph edge
        :param link:
        :return:
        """

        def get_bandwidth(if_list):
            """
            Calculate bandwidth for list of interfaces
            :param if_list:
            :return: total in bandwidth, total out bandwidth
            """
            in_bw = 0
            out_bw = 0
            for iface in if_list:
                bw = iface.get("bandwidth") or 0
                in_speed = iface.get("in_speed") or 0
                out_speed = iface.get("out_speed") or 0
                in_bw += bandwidth(in_speed, bw)
                out_bw += bandwidth(out_speed, bw)
            return in_bw, out_bw

        def bandwidth(speed, if_bw):
            if speed and if_bw:
                return min(speed, if_bw)
            elif speed and not if_bw:
                return speed
            elif if_bw:
                return if_bw
            else:
                return 0

        if link.is_loop:
            return  # Loops are not shown on map
            # Group interfaces by objects
            # avoiding non-bulk dereferencing
        mo_ifaces = defaultdict(list)
        for if_id in link.interface_ids:
            iface = self._interface_cache[if_id]
            mo_ifaces[self.G.nodes[str(iface["managed_object"])]["mo"]] += [iface]
        # Pairs of managed objects are pseudo-links
        if len(mo_ifaces) == 2:
            # ptp link
            pseudo_links = [list(mo_ifaces)]
            is_pmp = False
        else:
            # pmp
            # Create virtual cloud
            self.add_node(
                TopologyNode(
                    id=str(link.id),
                    title=str(link),
                    type="cloud",
                    stencil=stencil_registry.DEFAULT_CLOUD_STENCIL,
                )
            )
            # Create virtual links to cloud
            pseudo_links = [(link, mo) for mo in mo_ifaces]
            # Create virtual cloud interface
            mo_ifaces[link] = [{"name": "cloud"}]
            is_pmp = True
        # Link all pairs
        for mo0, mo1 in pseudo_links:
            mo0_id = str(mo0.id)
            mo1_id = str(mo1.id)
            # Create virtual ports for mo0
            self.G.nodes[mo0_id]["ports"] += [
                {"id": self.pn, "ports": [i["name"] for i in mo_ifaces[mo0]]}
            ]
            # Create virtual ports for mo1
            self.G.nodes[mo1_id]["ports"] += [
                {"id": self.pn + 1, "ports": [i["name"] for i in mo_ifaces[mo1]]}
            ]
            # Calculate bandwidth
            t_in_bw, t_out_bw = get_bandwidth(mo_ifaces[mo0])
            d_in_bw, d_out_bw = get_bandwidth(mo_ifaces[mo1])
            in_bw = bandwidth(t_in_bw, d_out_bw) * 1000
            out_bw = bandwidth(t_out_bw, d_in_bw) * 1000
            # Add link
            if is_pmp:
                link_id = "%s-%s-%s" % (link.id, self.pn, self.pn + 1)
            else:
                link_id = str(link.id)
            self.add_edge(
                mo0_id,
                mo1_id,
                {
                    "id": link_id,
                    "type": "link",
                    "method": link.discovery_method,
                    "ports": [self.pn, self.pn + 1],
                    # Target to source
                    "in_bw": in_bw,
                    # Source to target
                    "out_bw": out_bw,
                    # Max bandwidth
                    "bw": max(in_bw, out_bw),
                },
            )
            self.pn += 2

    def add_parent(self, parent, child):
        """
        Add Child-Parent link
        :param parent:
        :param child:
        :return:
        """
        # Create virtual ports
        if {"id": f"{parent}-children", "ports": ["children"]} not in self.G.nodes[child]["ports"]:
            self.G.nodes[parent]["ports"] += [{"id": f"{parent}-children", "ports": ["children"]}]
        self.G.nodes[child]["ports"] += [{"id": f"{child}-parent", "ports": ["parent"]}]
        self.add_edge(
            child,
            parent,
            {
                "id": f"{child}-{parent}",
                "ports": [f"{child}-parent", f"{parent}-children"],
                "connector": "smooth",
            },
            edge_type="parent",
        )

    def load(self):
        """
        Fill nodes and edges on graph
        :return:
        """
        ...

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

    def normalize_pos(
        self, pos: Dict[str, Tuple[int, int]]
    ) -> Tuple[int, int, Dict[str, Tuple[int, int]]]:
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
        """
        Getting layout module
        :return:
        """
        if not len(self.G):
            # Empty graph
            return SpringLayout
        if not self.settings.get("force_spring") and len(self.get_rings()) == 1:
            return RingLayout
        elif not self.settings.get("force_spring") and nx.is_forest(self.G):
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
        pos: Dict[str, Tuple[int, int]] = {o: pos[o] for o in pos if o in self.G.nodes}
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

    @staticmethod
    def q_node(node):
        """
        Format graph node
        :param node:
        :return:
        """
        x = node.copy()
        if "mo" in x:
            del x["mo"]
        if x["type"] == "managedobject":
            x["external"] = x.get("role") != "segment"
        elif node["type"] == "cloud":
            x["external"] = False
        return x

    def iter_nodes(self):
        """
        Iterate over map Nodes
        :return:
        """
        for n in self.G.nodes.values():
            yield self.q_node(n)

    def iter_edges(self) -> Iterable[Any]:
        """
        Iterate over map Edges
        :return:
        """
        for u, v in self.G.edges():
            yield self.G[u][v]

    @classmethod
    def is_empty(cls) -> bool:
        """Check if topology is empty."""
        return False

    @classmethod
    def iter_maps(
        cls,
        parent: str = None,
        query: Optional[str] = None,
        limit: Optional[int] = None,
        start: Optional[int] = None,
        page: Optional[int] = None,
    ) -> Iterable[MapItem]:
        """
        Iterator over available maps
        :param parent:
        :param query:
        :param limit:
        :param start:
        :param page:
        :return:
        """
        ...

    @classmethod
    def iter_path(cls, gen_id) -> Iterable[PathItem]:
        """
        Return map by hierarchy path
        :param gen_id:
        :return:
        """
        ...
