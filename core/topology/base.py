# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
#  BaseTopology class
# ----------------------------------------------------------------------
#  Copyright (C) 2007-2020 The NOC Project
#  See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator

# Third-Party modules
import six
from networkx import nx
import numpy as np
import cachetools

# NOC modules
from noc.core.stencil import stencil_registry
from noc.core.text import alnum_key
from .layout.ring import RingLayout
from .layout.spring import SpringLayout
from .layout.tree import TreeLayout


class BaseTopology(object):
    CAPS = {"Network | STP"}
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

    def __init__(self, node_hints=None, link_hints=None, force_spring=False):
        self.force_spring = force_spring
        #
        self.node_hints = node_hints or {}
        self.link_hints = link_hints or {}
        # Caches
        self._rings_cache = {}
        self._isolated_cache = {}
        # Graph
        self.G = nx.Graph()
        self.caps = set()
        self.load()

    def __len__(self):
        return len(self.G)

    def __contains__(self, item):
        return item.id in self.G

    def load(self):
        """
        Load objects and links
        """
        pass

    def get_role(self, mo):
        """
        Returns managed object's role.
        None if no role
        """
        return None

    def add_object(self, mo, attrs=None):
        """
        Add managed object to topology
        """
        attrs = attrs or {}
        mo_id = str(mo.id)
        if mo_id in self.G.node:
            # Only update attributes
            self.G.node[mo_id].update(attrs)
            return
        stencil = self.get_object_stencil(mo)
        # Get capabilities
        oc = set(mo.get_caps()) & self.CAPS
        self.caps |= oc
        # Apply node hints
        attrs.update(self.node_hints.get(mo_id) or {})
        # Apply default attributes
        attrs.update(
            {
                "mo": mo,
                "type": "managedobject",
                "id": mo_id,
                "name": mo.name,
                "address": mo.address,
                "role": self.get_role(mo),
                "shape": getattr(stencil, "path", ""),
                "shape_width": getattr(stencil, "width", 0),
                "shape_height": getattr(stencil, "height", 0),
                "level": mo.object_profile.level,
                "ports": [],
                "caps": list(oc),
            }
        )
        self.G.add_node(mo_id, **attrs)

    def add_cloud(self, link, attrs=None):
        """
        Add cloud to topology
        :param link:
        :param attrs:
        :return:
        """
        attrs = attrs or {}
        link_id = str(link.id)
        if link_id in self.G.node:
            # Only update attributes
            self.G.node[link_id].update(attrs)
            return
        stencil = self.get_cloud_stencil(link)
        # Apply node hints
        attrs.update(self.node_hints.get(link_id) or {})
        # Apply default attributes
        attrs.update(
            {
                "link": link,
                "type": "cloud",
                "id": link_id,
                "name": link.name or "",
                "ports": [],
                "shape": getattr(stencil, "path", ""),
                "shape_width": getattr(stencil, "width", 0),
                "shape_height": getattr(stencil, "height", 0),
            }
        )
        self.G.add_node(link_id, **attrs)

    def add_link(self, o1, o2, attrs=None):
        """
        Add link between interfaces to topology
        """
        a = {"connector": "normal"}
        if attrs:
            a.update(attrs)
        a.update({"type": "link"})
        #
        self.G.add_edge(o1, o2, **a)

    @staticmethod
    def get_object_stencil(mo):
        if mo.shape:
            # Use mo's shape, if set
            shape_id = mo.shape
        elif mo.object_profile.shape:
            # Use profile's shape
            shape_id = mo.object_profile.shape
        else:
            shape_id = None
        return stencil_registry.get(shape_id)

    @staticmethod
    def get_cloud_stencil(link):
        return stencil_registry.get(link.shape or stencil_registry.DEFAULT_CLOUD_STENCIL)

    def order_nodes(self, uplink, downlinks):
        """
        Sort downlinks basing on uplink's interface
        :param uplink: managed object id
        :param downlinks: ids of downlinks
        :returns: sorted list of downlinks
        """
        id_to_name = {}
        dl_map = {}  # downlink -> uplink port
        for p in self.G.node[uplink]["ports"]:
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
        return self.G.subgraph([o for o in self.G.node if o not in isolated])

    def normalize_pos(self, pos):
        """
        Normalize positions, shift to (0, 0).
        Returns width, height, post
        """
        maxv = np.array([0, 0])
        minv = np.array([0, 0])
        for p in six.itervalues(pos):
            maxv = np.maximum(maxv, p)
            minv = np.minimum(minv, p)
        # Dimensions
        s = maxv - minv
        # Shift positions according to offset and node size
        for p in pos:
            so = np.array(
                [self.G.node[p]["shape_width"] / 2.0, self.G.node[p]["shape_height"] / 2.0]
            )
            pos[p] -= minv + so - self.MAP_OFFSET
        return s[0], s[1], pos

    def get_layout_class(self):
        if not len(self.G):
            # Empty graph
            return SpringLayout
        if not self.force_spring and len(self.get_rings()) == 1:
            return RingLayout
        elif not self.force_spring and nx.is_forest(self.G):
            return TreeLayout
        else:
            return SpringLayout

    def layout(self):
        # Use node hints
        dpos = {}
        for p, nh in six.iteritems(self.node_hints):
            if "x" in nh and "y" in nh:
                dpos[p] = np.array([nh["x"], nh["y"]])
        if len(dpos) != len(self.G) and len(self.G):
            # Build layout
            pos = self.get_layout_class()(self).get_layout()
            pos.update(dpos)
        else:
            pos = dpos
        pos = dict((o, pos[o]) for o in pos if o in self.G.node)
        width, height, pos = self.normalize_pos(pos)
        # Place isolated nodes
        isolated = sorted((o for o in self.G if o not in pos), key=lambda x: self.G.node[x]["name"])
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
            self.G.node[o]["x"] = x
            self.G.node[o]["y"] = y
        # Calculate link positions
        for u, v in self.G.edges():
            ed = self.G[u][v]
            if ed["id"] in self.link_hints:
                # Use existing hints
                ed.update(self.link_hints)
            else:
                # @todo: Calculate new positions
                pass
