# ---------------------------------------------------------------------
# Topology processing
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Set, Optional, Tuple, Dict, Iterable
from logging import getLogger
import time
from collections import defaultdict

# Third-party modules
import networkx as nx

# NOC Modules
from noc.core.perf import metrics
from .types import ObjectSnapshot

logger = getLogger(__name__)


class Topo(object):
    """
    Topology processing class.

    Attributes:
        check: Check if uplink is really adjaced to node.
    """

    def __init__(self, check: bool = False):
        self.check = check
        self.graph = nx.Graph()
        self.dirty_nodes: Set[int] = set()
        metrics["obj_dirty"] = 0

    def sync_object(self, obj: ObjectSnapshot) -> None:
        """
        Synchronize object snapshot with topology.

        Apply object snapshot to topology, manipulating
        new nodes and edges when nesessary.

        Args:
            obj: Managed object snapshot
        """
        # @todo: Remove object
        # Synchronize object
        if obj.id in self.graph:
            self.update_object(obj)
        else:
            self.add_object(obj)
        # Synchronize links
        old_neighbors: Set[int] = set(self.graph.adj[obj.id])
        new_neighbors: Set[int] = set(obj.links) if obj.links else set()
        # Add new links
        for n in new_neighbors - old_neighbors:
            self.add_link(obj.id, n)
        # Remove links
        for n in old_neighbors - new_neighbors:
            self.remove_link(obj.id, n)
        # Update statistics
        metrics["obj"] = len(self.graph.nodes)
        # Too expensive calculate
        # metrics["links"] = len(self.graph.edges)

    def has_dirty(self) -> bool:
        """
        Check if topology has dirty node.

        Returns:
            True, if topology has dirty nodes and
            should be recalculated.
        """
        return bool(self.dirty_nodes)

    def set_dirty(self, obj: int) -> None:
        """
        Set objects' dirty status.

        Mark managed object as dirty to process
        topology on the next cycle.

        Args:
            obj: Managed Object's id.
        """
        self.dirty_nodes.add(obj)
        metrics["obj_dirty"] = len(self.dirty_nodes)

    def reset_dirty(self) -> None:
        """
        Reset all dirty objects.

        Clean dirty status on all objects.
        """
        self.dirty_nodes = set()
        metrics["obj_dirty"] = 0

    def add_object(self, obj: ObjectSnapshot) -> None:
        """
        Add object to topology.

        Args:
            obj: Managed object's snapshot.
        """
        self.graph.add_node(
            obj.id,
            level=obj.level,
            uplinks=self.clear_uplinks(obj.uplinks),
        )
        metrics["obj_add"] += 1
        metrics["obj_level", ("level", obj.level)] += 1
        self.set_dirty(obj.id)

    @staticmethod
    def clear_uplinks(s: Optional[Iterable[int]]) -> Optional[Tuple[int, ...]]:
        """
        Normalize uplinks.

        Args:
            s: Optional list of uplinks.

        Returns:
            Normalized uplinks.
        """
        return tuple(sorted(s)) if s else None

    @staticmethod
    def to_set(s: Optional[Set[int]]) -> Set[int]:
        """
        Normalize None, Tuple or Set to Set

        Args:
            s: Either None, Tuple or Set

        Returns:
            Set
        """
        if isinstance(s, set):
            return s
        if not s:
            return set()
        return set(s)

    def update_object(self, obj: ObjectSnapshot) -> None:
        """
        Update existing object with snapshot.

        Compare existing object with snapshot and apply
        changes when necessary.

        Args:
            obj: Managed object's snapshot.
        """
        node = self.graph.nodes[obj.id]
        changed = False
        if obj.level != node["level"]:
            node["level"] = obj.level
            changed = True
            metrics["obj_level", ("level", node["level"])] -= 1
            metrics["obj_level", ("level", obj.level)] += 1
        if self.to_set(node["uplinks"]) != self.to_set(obj.uplinks):
            node["uplinks"] = self.clear_uplinks(obj.uplinks)
            changed = True
        if changed:
            self.set_dirty(obj.id)
        metrics["obj_update"] += 1

    def remove_object(self, obj_id: int) -> None:
        """
        Remove Managed Object from topology.
        """
        if obj_id not in self.graph:
            return
        for adj in self.graph[obj_id]:
            self.set_dirty(adj)
        node = self.graph.nodes[obj_id]
        self.graph.remove_node(obj_id)
        metrics["obj_level", ("level", node["level"])] -= 1
        metrics["obj_remove"] += 1

    def add_link(self, u: int, v: int) -> None:
        """
        Add link between managed objects.

        Args:
            u: Local managed object.
            v: Remote managed object.
        """
        if u not in self.graph or v not in self.graph:
            # Will be created later
            metrics["obj_lookahead"] += 1
            return
        self.graph.add_edge(u, v)
        metrics["links_add"] += 1
        self.set_dirty(u)
        self.set_dirty(v)

    def remove_link(self, u: int, v: int) -> None:
        """
        Remove link from topology.

        Args:
            u: Local managed object.
            v: Remote managed object.
        """
        self.graph.remove_edge(u, v)
        metrics["links_remove"] += 1
        self.set_dirty(u)
        self.set_dirty(v)

    def process(self) -> Set[int]:
        """
        Proceess topology.

        Returns:
            Set of affected nodes.
        """
        logger.info("Processing topology")
        if not self.dirty_nodes:
            logger.info("No dirty nodes, stopping")
            return set()
        logger.info("%d dirty nodes found", len(self.dirty_nodes))
        t0 = time.time()
        affected: Set[int] = set()
        total_clusters = 0
        processed = 0
        for cc in nx.connected_components(self.graph):
            total_clusters += 1
            if self.is_dirty(cc):
                processed += 1
                for n, uplinks in self.iter_connected_cluster_uplinks(cc):
                    node = self.graph.nodes[n]
                    if self.check:
                        # Check uplink is valid
                        adj_set = set(self.graph[n])
                        if not uplinks.issubset(adj_set):
                            logger.error(
                                "Invalid uplinks for %s. %s is not subset of %s",
                                n,
                                uplinks,
                                adj_set,
                            )
                            metrics["uplink_not_adj"] += 1
                            continue
                    current = self.to_set(node["uplinks"])
                    if current != uplinks:
                        logger.info(
                            "Uplinks changed for %d: {%s} -> {%s}",
                            n,
                            self.to_join(current),
                            self.to_join(uplinks),
                        )
                        affected.add(n)
                        affected |= current
                        affected |= uplinks
                        # Fix uplinks on graph
                        node["uplinks"] = self.clear_uplinks(uplinks)
        if affected:
            logger.info("%d affected objects detected", len(affected))
            metrics["obj_topo_affected"] += len(affected)
        self.reset_dirty()
        dt = time.time() - t0
        logger.info("Processed %d clusters of %d in %2fs", processed, total_clusters, dt)
        metrics["clusters"] = total_clusters
        metrics["clusters_processed"] += processed
        return affected

    def iter_uplinks(self, root: int, uplinks: Dict[int, Set[int]]) -> Iterable[Tuple[int, int]]:
        """
        Iterate over all uplinks leading to root.

        Build all possible paths from root to every connected
        node. Based on NetworkX all_simple_path function
        optimized to our case.

        Args:
            root: Id of the root node.
            uplinks: Dict of node id, set of uplinks, collected for previous roots.

        Returns:
            Yields tuple of node id, uplink id
        """
        visited = {root: True}
        stack = [iter(self.graph[root])]
        while stack:
            child = next(stack[-1], None)
            if child is None:
                stack.pop()
                visited.popitem()
                continue
            # Get last appended element
            uplink, _ = visited.popitem()
            visited[uplink] = True
            if uplink in uplinks[child]:
                # This path has been traversed from other root.
                # No new uplinks there and below.
                continue
            yield child, uplink
            next_nodes = set(self.graph[child]) - set(visited)
            if next_nodes:
                visited[child] = True
                stack.append(iter(next_nodes))

    def is_dirty(self, cc: Set[int]) -> bool:
        """
        Check if cluster is dirty ad should be recalculated.

        Args:
            cc: Set of cluster members.

        Returns:
            * True - if cluster contains dirty nodes
                and should be recalculated.
            * False - cluster is clear.
        """
        return len(cc.intersection(self.dirty_nodes)) > 0

    def iter_connected_cluster_uplinks(self, cc: Set[int]) -> Iterable[Tuple[int, Set[int]]]:
        """
        Iterate over all uplinks of cluster.

        Detect root nodes and build all paths to all cluster nodes.

        Args:
            cc: Set of managed object ids forming a cluster
                (conected component)

        Returns:
            Yields tuple of `node id`, set of uplinks.
        """
        power = len(cc)
        if power == 1:
            # Isolate, Reset uplinks
            for node in cc:
                yield node, set()
            return
        # Get max level
        # @todo: Optimize, search for roots
        min_level = min(self.graph.nodes[n]["level"] for n in cc)
        max_level = max(self.graph.nodes[n]["level"] for n in cc)
        logger.debug("Cluster contains %d nodes. Levels %d..%d", power, min_level, max_level)
        if min_level == max_level:
            # Single ranged cluster, all are roots
            roots = cc
        else:
            roots = {n for n in cc if self.graph.nodes[n]["level"] == max_level}
        logger.debug("Roots: %s at level %d", self.to_join(roots), max_level)
        uplinks = defaultdict(set)
        if len(roots) == 1:
            uplinks[list(roots)[0]] = set()
        for root in roots:
            logger.debug("Processing from root %s", root)
            for node, uplink in self.iter_uplinks(root, uplinks):
                uplinks[node].add(uplink)
        logger.debug("Found uplinks for %d objects", len(uplinks))
        yield from uplinks.items()

    def get_uplinks(self, obj: int) -> Set[int]:
        """
        Get node uplinks.

        Args:
            obj: Managed object's uplink.

        Returns:
            Set of object uplinks
        """
        uplinks = self.graph.nodes[obj]["uplinks"]
        if uplinks:
            return set(uplinks)
        return set()

    def get_rca_neighbors(self, obj: int) -> Set[int]:
        """
        Get RCA neighbors.

        Args:
            obj: Managed object's uplink.

        Returns:
            List of RCA neighbors.
        """
        uplinks = self.get_uplinks(obj)
        r: Set[int] = set()
        for n in self.graph[obj]:
            r.add(n)
            if n not in uplinks:
                r |= self.get_uplinks(n)
        return r - {obj}

    @staticmethod
    def to_join(ids: Iterable[int]) -> str:
        return ", ".join([str(x) for x in sorted(ids)])
