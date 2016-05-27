# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BaseTopology class
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from collections import defaultdict
## Third-Party modules
from networkx import nx
## NOC modules
from noc.lib.stencil import stencil_registry
from noc.lib.text import split_alnum


class BaseTopology(object):
    def __init__(self, node_hints=None, link_hints=None):
        self.node_hints = node_hints or {}
        self.link_hints = link_hints or {}
        self.G = nx.Graph()
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
        shape = self.get_object_shape(mo)
        sw, sh = self.get_shape_size(shape)
        # Apply node hints
        attrs.update(self.node_hints.get(mo.id) or {})
        # Apply default attributes
        attrs.update({
            "mo": mo,
            "type": "managedobject",
            "id": mo.id,
            "name": mo.name,
            "role": self.get_role(mo),
            "shape": shape,
            "shape_width": sw,
            "shape_height": sh,
            "level": mo.object_profile.level,
            "ports": []
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

    def get_object_shape(self, mo):
        if mo.shape:
            # Use mo's shape, if set
            sn = mo.shape
        elif mo.object_profile.shape:
            # Use profile's shape
            sn = mo.object_profile.shape
        else:
            # Fallback to router shape
            sn = "Cisco/router"
        return sn

    def get_shape_size(self, shape):
        return stencil_registry.get_size(shape)

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
            for p in  self.G.edge[uplink][dl]["ports"]:
                if p in id_to_name:
                    dl_map[dl] = id_to_name[p]
                    break
        return sorted(dl_map, key=lambda x: split_alnum(dl_map[x]))

