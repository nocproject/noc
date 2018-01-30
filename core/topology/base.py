# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
#  BaseTopology class
# ----------------------------------------------------------------------
#  Copyright (C) 2007-2018 The NOC Project
#  See LICENSE for details
# ----------------------------------------------------------------------

# Third-Party modules
from networkx import nx
# NOC modules
from noc.core.stencil import stencil_registry
from noc.lib.text import split_alnum


class BaseTopology(object):
    CAPS = set([
        "Network | STP"
    ])

    def __init__(self, node_hints=None, link_hints=None):
        self.node_hints = node_hints or {}
        self.link_hints = link_hints or {}
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
        if mo.id in self.G.node:
            # Only update attributes
            self.G.node[mo.id].update(attrs)
            return
        stencil = self.get_object_stencil(mo)
        # Get capabilities
        oc = set(mo.get_caps()) & self.CAPS
        self.caps |= oc
        # Apply node hints
        attrs.update(self.node_hints.get(mo.id) or {})
        # Apply default attributes
        attrs.update({
            "mo": mo,
            "type": "managedobject",
            "id": mo.id,
            "name": mo.name,
            "address": mo.address,
            "role": self.get_role(mo),
            "shape": stencil.path,
            "shape_width": stencil.width,
            "shape_height": stencil.height,
            "level": mo.object_profile.level,
            "ports": [],
            "caps": list(oc)
        })
        self.G.add_node(mo.id, attrs)

    def add_link(self, o1, o2, attrs=None):
        """
        Add link between interfaces to topology
        """
        a = {
            "connector": "normal"
        }
        if attrs:
            a.update(attrs)
        a.update({
            "type": "link"
        })
        #
        self.G.add_edge(o1, o2, a)

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
            id_to_name[p["id"]] = sorted(p["ports"], key=split_alnum)[0]
        for dl in downlinks:
            for p in self.G.edge[uplink][dl]["ports"]:
                if p in id_to_name:
                    dl_map[dl] = id_to_name[p]
                    break
        return sorted(dl_map, key=lambda x: split_alnum(dl_map[x]))
