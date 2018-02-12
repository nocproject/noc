# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
#  SegmentTopology class
# ----------------------------------------------------------------------
#  Copyright (C) 2007-2018 The NOC Project
#  See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import operator
import logging
import itertools
from collections import defaultdict
# Third-party modules
import networkx as nx
import numpy as np
from cachetools import cachedmethod
import six
# NOC modules
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link
from .base import BaseTopology
from .layout.ring import RingLayout
from .layout.spring import SpringLayout
from .layout.tree import TreeLayout

logger = logging.getLogger(__name__)


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
        self.segment_siblings = self.segment.get_siblings()
        self._uplinks_cache = {}
        self._rings_cache = {}
        self._isolated_cache = {}
        self.force_spring = force_spring
        self.segment_objects = set()
        if self.segment.parent:
            self.parent_segment = self.segment.parent
            self.ancestor_segments = set(self.segment.get_path()[:-1])
        else:
            self.parent_segment = None
            self.ancestor_segments = set()
        super(SegmentTopology, self).__init__(node_hints, link_hints)

    def get_role(self, mo):
        if mo.segment in self.segment_siblings:
            return "segment"
        elif self.parent_segment and mo.segment.id in self.ancestor_segments:
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

        # Get all links, belonging to segment
        links = list(Link.objects.filter(
            linked_segments__in=[s.id for s in self.segment_siblings])
        )
        # All linked interfaces from map
        all_ifaces = list(
            itertools.chain.from_iterable(
                link.interface_ids for link in links
            )
        )
        # Bulk fetch all interfaces data
        ifs = dict((i["_id"], i) for i in Interface._get_collection().find(
            {
                "_id": {
                    "$in": all_ifaces
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
        # Bulk fetch all managed objects
        segment_mos = set(self.segment.managed_objects.values_list("id", flat=True))
        all_mos = list(
            set(i["managed_object"] for i in six.itervalues(ifs) if "managed_object" in i) |
            segment_mos
        )
        mos = dict(
            (mo.id, mo)
            for mo in ManagedObject.objects.filter(id__in=all_mos)
        )
        self.segment_objects = set(
            mo_id for mo_id in all_mos
            if mos[mo_id].segment.id == self.segment.id
        )
        for mo in six.itervalues(mos):
            self.add_object(mo)
        # Process all segment's links
        pn = 0
        for link in links:
            if link.is_loop:
                continue  # Loops are not shown on map
            # Group interfaces by objects
            # avoiding non-bulk dereferencing
            mo_ifaces = defaultdict(list)
            for if_id in link.interface_ids:
                iface = ifs[if_id]
                mo_ifaces[mos[iface["managed_object"]]] += [iface]
            # Pairs of managed objects are pseudo-links
            if len(mo_ifaces) == 2:
                # ptp link
                pseudo_links = [list(mo_ifaces)]
                is_pmp = False
            else:
                # pmp
                # Create virtual cloud
                self.add_cloud(link)
                # Create virtual links to cloud
                pseudo_links = [(link, mo) for mo in mo_ifaces]
                # Create virtual cloud interface
                mo_ifaces[link] = [{
                    "name": "cloud"
                }]
                is_pmp = True
            # Link all pairs
            for mo0, mo1 in pseudo_links:
                mo0_id = str(mo0.id)
                mo1_id = str(mo1.id)
                # Create virtual ports for mo0
                self.G.node[mo0_id]["ports"] += [{
                    "id": pn,
                    "ports": [i["name"] for i in mo_ifaces[mo0]]
                }]
                # Create virtual ports for mo1
                self.G.node[mo1_id]["ports"] += [{
                    "id": pn + 1,
                    "ports": [i["name"] for i in mo_ifaces[mo1]]
                }]
                # Calculate bandwidth
                t_in_bw, t_out_bw = get_bandwidth(mo_ifaces[mo0])
                d_in_bw, d_out_bw = get_bandwidth(mo_ifaces[mo1])
                in_bw = bandwidth(t_in_bw, d_out_bw) * 1000
                out_bw = bandwidth(t_out_bw, d_in_bw) * 1000
                # Add link
                if is_pmp:
                    link_id = "%s-%s-%s" % (link.id, pn, pn + 1)
                else:
                    link_id = str(link.id)
                self.add_link(mo0_id, mo1_id, {
                    "id": link_id,
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
        for p, nh in self.node_hints.iteritems():
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
        isolated = sorted((o for o in self.G if o not in pos),
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
        Shortest path first
        """
        def get_node_uplinks(node):
            ups = {}
            for u in uplinks:
                for path in nx.all_simple_paths(self.G, node, u):
                    lp = len(path)
                    p = path[1]
                    ups[p] = min(lp, ups.get(p, lp))
            # Shortest path first
            return sorted(ups, key=lambda x: ups[x])

        uplinks = self.get_uplinks()
        # Get all cloud nodes
        cloud_nodes = [o for o in self.G.node if self.G.node[o]["type"] == "cloud"]
        # Get uplinks for cloud nodes
        cloud_uplinks = dict(
            (o, [int(u) for u in get_node_uplinks(o)])
            for o in cloud_nodes
        )
        # Get all segment objects' nodes
        segment_objects = set(str(o) for o in self.segment_objects)  # Convert to string
        # Get objects uplinks
        r = {}
        for o in segment_objects:
            ups = []
            for u in get_node_uplinks(o):
                cu = cloud_uplinks.get(u)
                if cu:
                    # Uplink is a cloud. Use cloud's uplinks instead
                    ups += cu
                else:
                    ups += [int(u)]
            r[int(o)] = ups
        return r


def update_uplinks(segment_id):
    from noc.inv.models.networksegment import NetworkSegment
    from noc.sa.models.objectdata import ObjectData

    segment = NetworkSegment.get_by_id(segment_id)
    if not segment:
        logger.warning("Segment with id: %s does not exist" % segment_id)
        return

    st = SegmentTopology(segment)
    ObjectData.update_uplinks(
        st.get_object_uplinks()
    )
