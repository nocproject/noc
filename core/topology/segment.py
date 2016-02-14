# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SegmentTopology class
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import operator
import operator
## Third-party modules
import networkx as nx
import numpy as np
from cachetools import cachedmethod
## NOC modules
from base import BaseTopology
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link
from layout.ring import RingLayout
from layout.spring import SpringLayout


class SegmentTopology(BaseTopology):
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

    def __init__(self, segment, node_hints=None, link_hints=None,
                 force_spring=False):
        self.segment = segment
        self._uplinks_cache = {}
        self._rings_cache = {}
        self._isolated_cache = {}
        self.force_spring = force_spring
        if self.segment.parent:
            self.parent_segment = self.segment.parent
        else:
            self.parent_segment = None
        super(SegmentTopology, self).__init__(node_hints, link_hints)

    def get_role(self, mo):
        if mo.segment.id == self.segment.id:
            return "segment"
        elif mo.segment.id == self.parent_segment.id:
            return "uplink"
        else:
            return "downlink"

    @cachedmethod(operator.attrgetter("_uplinks_cache"))
    def get_uplinks(self):
        r = []
        for i in self.G.node:
            if self.G.node[i].get("role") == "uplink":
                r += [i]
        return r

    @cachedmethod(operator.attrgetter("_rings_cache"))
    def get_rings(self):
        """
        Return list of all rings
        """
        return list(nx.cycle_basis(self.G))

    @cachedmethod(operator.attrgetter("_isolated_cache"))
    def get_isolated(self):
        """
        Returns list of nodes without connections
        """
        return list(nx.isolates(self.G))

    def non_isolated_graph(self):
        isolated = set(self.get_isolated())
        return self.G.subgraph([o for o in self.G.node if o not in isolated])

    def load(self):
        """
        Load all managed objects from segment
        """
        def bandwidth(speed, bandwidth):
            if speed and bandwidth:
                return min(speed, bandwidth)
            elif speed and not bandwidth:
                return speed
            elif bandwidth:
                return bandwidth
            else:
                return 0

        # Get segment's objects
        mos = list(self.segment.managed_objects)
        for o in mos:
            self.add_object(o)
        # Get all interfaces
        ifs = dict((i["_id"], i) for i in Interface._get_collection().find(
            {
                "managed_object": {
                    "$in": [o.id for o in mos]
                },
                "type": {
                    "$in": ["physical", "management"]
                }
            },
            {
                "_id": 1,
                "managed_object": 1,
                "name": 1,
                "bandwidth": 1,
                "in_speed": 1,
                "out_speed": 1
            }
        ))
        # Get all links
        pn = 0
        for link in Link.objects.filter(interfaces__in=list(ifs)):
            mos = set()
            for i in link.interfaces:
                mos.add(i.managed_object)
            if len(mos) != 2:
                continue
            # Add objects
            m0 = mos.pop()
            m1 = mos.pop()
            i0, i1 = [], []
            for i in link.interfaces:
                if i.managed_object == m0:
                    i0 += [i]
                else:
                    i1 += [i]
            self.add_object(m0)
            self.G.node[m0.id]["ports"] += [{
                "id": pn,
                "ports": [i.name for i in i0]
            }]
            self.add_object(m1)
            self.G.node[m1.id]["ports"] += [{
                "id": pn + 1,
                "ports": [i.name for i in i1]
            }]
            # Add link
            t_in_bw = 0
            t_out_bw = 0
            for i in i0:
                iface = ifs.get(i.id) or {}
                bw = iface.get("bandwidth") or 0
                in_speed = iface.get("in_speed") or 0
                out_speed = iface.get("out_speed") or 0
                t_in_bw += bandwidth(in_speed, bw)
                t_out_bw += bandwidth(out_speed, bw)
            d_in_bw = 0
            d_out_bw = 0
            for i in i1:
                iface = ifs.get(i.id) or {}
                bw = iface.get("bandwidth") or 0
                in_speed = iface.get("in_speed") or 0
                out_speed = iface.get("out_speed") or 0
                d_in_bw += bandwidth(in_speed, bw)
                d_out_bw += bandwidth(out_speed, bw)
            in_bw = bandwidth(t_in_bw, d_out_bw) * 1000
            out_bw = bandwidth(t_out_bw, d_in_bw) * 1000
            self.add_link(m0.id, m1.id, {
                "id": str(link.id),
                "type": "link",
                "method": link.discovery_method,
                "ports": [pn, pn + 1],
                # Target to source
                "in_bw": in_bw,
                # Source to target
                "out_bw": out_bw,
                # Max bandwidth
                "bw": max(in_bw, out_bw)
            })
            pn += 2

    def max_uplink_path_len(self):
        """
        Returns a maximum path length to uplink
        """
        n = 0
        uplinks = self.get_uplinks()
        for u in uplinks:
            for o in self.G.node:
                if o not in uplinks:
                    for p in nx.all_simple_paths(self.G, o, u):
                        n = max(n, len(p))
        return n

    def normalize_pos(self, pos):
        """
        Normalize positions, shift to (0, 0).
        Returns width, height, post
        """
        maxv = np.array([0, 0])
        minv = np.array([0, 0])
        for p in pos.itervalues():
            maxv = np.maximum(maxv, p)
            minv = np.minimum(minv, p)
        # Dimensions
        s = maxv - minv
        # Shift positions according to offset and node size
        for p in pos:
            so = np.array([
                self.G.node[p]["shape_width"] / 2.0,
                self.G.node[p]["shape_height"] / 2.0
            ])
            pos[p] -= minv + so - self.MAP_OFFSET
        return s[0], s[1], pos

    def get_layout_class(self):
        # @todo: Tree  nx.is_forest(..)
        if not self.force_spring and len(self.get_rings()) == 1:
            return RingLayout
        else:
            return SpringLayout

    def layout(self):
        # Use node hints
        dpos = {}
        for p, nh in self.node_hints.iteritems():
            if "x" in nh and "y" in nh:
                dpos[p] = np.array([nh["x"], nh["y"]])
        if len(dpos) != len(self.G):
            # Build layout
            pos = self.get_layout_class()(self).get_layout()
            pos.update(dpos)
        else:
            pos = dpos
        width, height, pos = self.normalize_pos(pos)
        # Place isolated nodes
        isolated = sorted((o for o in self.get_isolated()),
                          key=lambda x: self.G.node[x]["name"])
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

    def get_object_uplinks(self):
        """
        Returns a dict of <object id> -> [<uplink object id>, ...]
        """
        uplinks = self.get_uplinks()
        r = {}
        for o in self.G.node:
            if o in uplinks:
                continue
            ups = set()
            for u in uplinks:
                paths = list(nx.all_simple_paths(self.G, o, u))
                if paths:
                    ups |= set(p[1] for p in paths)
            r[o] = sorted(ups)
        return r


def update_uplinks(segment_id):
    from noc.inv.models.networksegment import NetworkSegment
    from noc.inv.models.objectuplink import ObjectUplink

    try:
        segment = NetworkSegment.objects.get(id=segment_id)
    except NetworkSegment.DoesNotExist:
        return
    st = SegmentTopology(segment)
    st.load()
    ObjectUplink.update_uplinks(
        st.get_object_uplinks()
    )
