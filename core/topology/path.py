# ----------------------------------------------------------------------
# Path tracing utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict
import operator

# Third-party modules
from typing import Optional, Iterable, List, Dict, Set, Tuple, DefaultDict, NamedTuple
from bson import ObjectId

# NOC modules
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.link import Link
from noc.sa.models.managedobject import ManagedObject
from .goal.base import BaseGoal
from .goal.managedobject import ManagedObjectGoal
from .constraint.base import BaseConstraint

MAX_PATH_LENGTH = 0xFFFFFFFF
PathInfo = NamedTuple(
    "PathInfo",
    [("start", ManagedObject), ("end", ManagedObject), ("links", List[Link]), ("l2_cost", int)],
)


def get_shortest_path(start: ManagedObject, goal: ManagedObject) -> List[ManagedObject]:
    """
    Returns a list of Managed Objects along shortest path
    using modified A* algorithm
    :param start: Starting managed object's id
    :param goal: Ending managed object's id
    :return:
    """
    finder = KSPFinder(start, ManagedObjectGoal(goal))
    r: List[ManagedObject] = []
    path = finder.find_shortest_path()
    if not path:
        raise ValueError("Path not found")
    for pi in path:  # type: PathInfo
        r += [pi.start]
    r += [pi.end]
    return r


class KSPFinder(object):
    """
    k-Shortest Path finder
    """

    def __init__(
        self,
        start: ManagedObject,
        goal: BaseGoal,
        constraint: Optional[BaseConstraint] = None,
        max_depth: Optional[int] = MAX_PATH_LENGTH,
        n_shortest: Optional[int] = 1,
    ) -> None:
        self.start: ManagedObject = start
        self.goal: BaseGoal = goal
        self.constraint: Optional[BaseConstraint] = constraint
        self.max_depth: Optional[int] = max_depth
        self.n_shortest: Optional[int] = n_shortest
        # Set of segments on path
        self.segments: Set[NetworkSegment] = set()
        # Managed Object cache
        self.mo_cache: Dict[int, ManagedObject] = {}
        # Links cache
        self.mo_links: DefaultDict[int, Set[Link]] = defaultdict(set)
        # Segments with valid cached links
        self.cached_seg_links: Set[ObjectId] = set()

    def find_shortest_path(self) -> List[PathInfo]:
        """
        Returns a list of Managed Objects along shortest path
        using modified A* algorithm

        :return:
        """
        return self._find_shortest_path(self.start)

    def _find_shortest_path(
        self,
        start: ManagedObject,
        pruned_links: Optional[List[ObjectId]] = None,
        max_depth: int = MAX_PATH_LENGTH,
    ) -> List[PathInfo]:
        """
        Returns a list of Managed Objects along shortest path
        using modified A* algorithm

        :param pruned_links: Set of links id to be excluded from path calculation
        :param max_depth: Depth limit search
        :return:
        """

        def max_path_length() -> int:
            return MAX_PATH_LENGTH

        def iter_neighbors(n_ids: Iterable[int]) -> Iterable[ManagedObject]:
            for m_id in n_ids:
                n_mo = self.mo_cache.get(m_id)
                if n_mo:
                    yield n_mo
                else:
                    n_mo = ManagedObject.get_by_id(m_id)
                    if n_mo:
                        self.mo_cache[n_mo.id] = n_mo
                        yield n_mo

        def is_allowed_link(current_mo: ManagedObject, link: Link) -> bool:
            if not self.constraint.is_valid_link(link):
                return False
            allow_egress = False
            allow_ingress = False
            for iface in link.interfaces:
                if iface.managed_object.id == current_mo.id:
                    # Egress
                    if not allow_egress:
                        allow_egress = self.constraint.is_valid_egress(iface)
                elif not allow_ingress:
                    allow_ingress = self.constraint.is_valid_ingress(iface)
                if allow_egress and allow_ingress:
                    return True
            return False

        def iter_links(current_mo: ManagedObject) -> Iterable[Link]:
            if (
                current_mo.id in self.mo_links
                and current_mo.segment.id not in self.cached_seg_links
            ):
                # Invalidate incomplete cache records for border objects
                del self.mo_links[current_mo.id]
            if current_mo.id not in self.mo_links:
                # Read all segment's links at once and fill the cache
                for link in Link.objects.filter(linked_segments=current_mo.segment.id):
                    for l_mo in link.linked_objects:
                        self.mo_links[l_mo].add(link)
                    self.cached_seg_links.add(current_mo.segment.id)
            for link in self.mo_links[current_mo.id]:
                # Prune excluded links
                if pruned_links and link.id in pruned_links:
                    continue
                if not self.constraint or is_allowed_link(current_mo, link):
                    yield link

        def reconstruct_path(goal_mo: ManagedObject) -> List[PathInfo]:
            obj_path = [goal_mo]  # type: List[ManagedObject]
            while True:
                goal_mo = came_from.get(goal_mo)
                if not goal_mo:
                    break
                obj_path.insert(0, goal_mo)
            full_path = []  # type: List[PathInfo]
            for mo1, mo2 in zip(obj_path, obj_path[1:]):
                links = [link for link in self.mo_links[mo1.id] if mo2.id in link.linked_objects]
                cost = min(link.l2_cost or 1 for link in links)
                full_path += [PathInfo(mo1, mo2, links, cost)]
            return full_path

        def current_path_len(current_mo: ManagedObject) -> int:
            n = 0
            while current_mo != start:
                current_mo = came_from.get(current_mo)
                assert current_mo
                n += 1
            return n

        # Effective search depth limitation
        max_depth = min(max_depth, self.max_depth)
        # Already evaluated nodes, contains MO ids
        closed_set = set()  # type: Set[int]
        # Currently discovered nodes than are not evaluated yet.
        # Start node is already known
        open_set = {start}  # type: Set[ManagedObject]
        # For each node, which node it can most efficiently be reached from.
        # If a node can be reached from many nodes, came_from will eventually contain the
        # most efficient previous step.
        came_from = {}  # type: Dict[ManagedObject, ManagedObject]
        # For each node, the cost of getting from the start node to that node.
        # Default value is infinity
        g_score = defaultdict(max_path_length)  # type: DefaultDict[ManagedObject, int]
        # The cost of going from start to start is zero.
        g_score[start] = 0
        # For each node, the total cost of getting from the start node to the goal
        # by passing by that node. That value is partly known, partly heuristic.
        f_score = defaultdict(max_path_length)  # type: Dict[ManagedObject, int]
        # For the first node, that value is completely heuristic.
        f_score[start] = self.goal.cost_estimate(start)
        # Find solution
        while open_set:
            # Current is the node in open_set having the lowest f_score value
            current = sorted(open_set, key=lambda x: f_score[x])[0]
            # If current matches goal, solution found
            if self.goal.is_goal(current):
                return reconstruct_path(current)
            # Move current from open_set to closed_set
            open_set.remove(current)
            closed_set.add(current.id)
            # Discard if drop cost
            if f_score[current] >= self.goal.DROP_COST:
                continue
            # Restrict path length
            if current_path_len(current) >= max_depth:
                continue
            # Get neighbors of current and their distances
            seen_neighbors = set()  # type: Set[int]
            dist = {}  # type: Dict[int, int]
            for ll in iter_links(current):
                new_neighbors = (
                    set(ll.linked_objects) - closed_set
                )  # Current is already in closed set
                seen_neighbors |= new_neighbors
                for mo in new_neighbors:
                    dist[mo] = 1  # min(l.l2_cost, dist.get(mo, MAX_PATH_LENGTH))
            # Evaluate neighbors
            for neighbor in iter_neighbors(seen_neighbors):
                if self.constraint and not self.constraint.is_valid_neighbor(current, neighbor):
                    continue  # Skip invalid neighbors
                if neighbor not in open_set:
                    open_set.add(neighbor)  # Discover a new node
                # The distance from start to a neighbor
                tentative_g_score = g_score[current] + dist[neighbor.id]
                if tentative_g_score >= g_score[neighbor]:
                    continue  # Not a better path
                # This path is best until now, record it
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + self.goal.cost_estimate(neighbor, current)
        raise ValueError("Path not found")

    def iter_shortest_paths(self) -> Iterable[List[PathInfo]]:
        """
        Returns a list of up to `n_shortest` shortest paths.
        Yen's algorithm applied to A*

        :return:
        """

        def to_path(path: List[PathInfo]) -> List[ManagedObject]:
            r: List[ManagedObject] = []
            for pi in path:
                r += [pi.start]
            r += [pi.end]
            return r

        def apply_pruned(path: List[PathInfo]) -> None:
            for pi in path:
                for link in pi.links:
                    pruned_links[pi.start].add(link.id)
                    pruned_links[pi.end].add(link.id)

        # Shortcut for one path
        A: List[PathInfo] = self._find_shortest_path(self.start)
        yield A
        if self.n_shortest == 1:
            return
        # Pruned links for each spur node
        pruned_links: DefaultDict[ManagedObject, Set[ObjectId]] = defaultdict(set)
        # Alternative paths
        B: List[Tuple[List[PathInfo], int]] = []
        #
        for k in range(1, self.n_shortest):
            apply_pruned(A)
            a_path = to_path(A)[:-2]
            for i, spur_node in enumerate(a_path):
                root_path = A[:i]
                try:
                    spur_path = self._find_shortest_path(
                        spur_node, pruned_links[spur_node], self.max_depth - i
                    )
                except ValueError:
                    continue
                total_path = root_path + spur_path
                B += [(total_path, sum(pi.l2_cost for pi in total_path))]
            if not B:
                break  # No alternative paths
            # Find best alternative path and add to result
            B = sorted(B, key=operator.itemgetter(1))
            A = B.pop(0)[0]
            yield A
