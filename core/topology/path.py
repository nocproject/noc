# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Path tracing utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict
# NOC modules
from noc.inv.models.link import Link
from noc.sa.models.managedobject import ManagedObject

MAX_PATH_LENGTH = 0xffffffff
SEGMENT_COST = 1
HORIZONTAL_COST = 3


def max_path_length():
    return MAX_PATH_LENGTH


def get_segment_path(start, goal):
    """
    Returns a list of segments laying between two management objects
    :param start: Managed Object instance
    :param goal: Managed Object instance
    :return: List of NetworkSegments
    """
    def merge_path(l1, l2, cross):
        ci = list(cross)[0]
        i1 = l1.index(ci)
        ri1 = l1[:i1]
        i2 = l2.index(ci)
        ri2 = list(reversed(l2[:i2]))
        return ri1 + [ci] + ri2

    p1 = [start.segment]
    p2 = [goal.segment]
    while True:
        can_up1 = bool(p1[-1].parent)
        can_up2 = bool(p2[-1].parent)
        c = set(p1) & set(p2)
        if c:
            return merge_path(p1, p2, c)
        # Up mo1 path
        if can_up1:
            p1 += [p1[-1].parent]
            c = set(p1) & set(p2)
            if c:
                return merge_path(p1, p2, c)
        # Up mo2 path
        if can_up2:
            p2 += [p2[-1].parent]
        elif not can_up2:
            raise ValueError("Cannot find path")


def get_shortest_path(start, goal):
    """
    Returns a list of Managed Objects along shortest path
    using modified A* algorihm
    :param start:
    :param goal:
    :return:
    """
    def reconstruct_path(came_from, current):
        total_path = [current]
        while True:
            current = came_from.get(current)
            if not current:
                break
            total_path.insert(0, current)
        return total_path

    def heuristic_cost_estimate(neighbor, goal):
        return hw[neighbor.segment]

    # We will restrict search only to segments along the path
    seg_path = get_segment_path(start, goal)
    s_seg_path = set(seg_path)
    # Heuristic weight is the number of segments to be passed to goal
    pl = len(seg_path)
    hw = {}
    for i, s in enumerate(seg_path):
        hw[s] = (pl - i) * SEGMENT_COST
    # Allow path via parent segment
    # if searching within one segment
    if len(seg_path) == 1 and seg_path[0].parent:
        s_seg_path.add(seg_path[0].parent)
        hw[seg_path[0].parent] = 2 * SEGMENT_COST
    # Already evaluated nodes
    closed_set = set()
    # Currently discovered nodes than are not evaluated yet.
    # Start node is already known
    open_set = set([start])
    # For each node, which node it can most efficiently be reached from.
    # If a node can be reached from many nodes, cameFrom will eventually contain the
    # most efficient previous step.
    came_from = {}
    # For each node, the cost of getting from the start node to that node.
    # Default value is infinity
    g_score = defaultdict(max_path_length)
    # The cost of going from start to start is zero.
    g_score[start] = 0
    # For each node, the total cost of getting from the start node to the goal
    # by passing by that node. That value is partly known, partly heuristic.
    f_score = defaultdict(max_path_length)
    # For the first node, that value is completely heuristic.
    f_score[start] = heuristic_cost_estimate(start, goal)
    # Find solution
    while open_set:
        # Current is the node in open_set having the lowest f_score value
        current = sorted(open_set, key=lambda x: f_score[x])[0]
        # If current matches goal, solution found
        if current == goal:
            return reconstruct_path(came_from, current)
        # Move current from open_set to closed_set
        open_set.remove(current)
        closed_set.add(current)
        # Get neighbors of current and their distances
        seen_neighbors = set()
        dist = {}
        for l in Link.objects.filter(linked_objects=current.id):
            for mo in l.linked_objects:
                if mo != current.id:
                    seen_neighbors.add(mo)
                    dist[mo] = min(l.l2_cost, dist.get(mo, MAX_PATH_LENGTH))
        neighbors = [ManagedObject.get_by_id(mo)
                     for mo in seen_neighbors]
        # Evaluate neighbors
        for neighbor in neighbors:
            if neighbor in closed_set:
                continue  # Already evaluated
            if neighbor.segment not in s_seg_path:
                if neighbor.segment.enable_horizontal_transit:
                    s_seg_path.add(neighbor.segment)
                    hw[neighbor.segment] = hw[current.segment] + HORIZONTAL_COST
                else:
                    # Try horizontal transit
                    continue  # Strip ways to unused segments
            if neighbor not in open_set:
                open_set.add(neighbor)  # Discover a new node
            # The distance from start to a neighbor
            tentative_g_score = g_score[current] + dist[neighbor.id]
            if tentative_g_score >= g_score[neighbor]:
                continue  # Not a better path
            # This path is best until now, record it
            came_from[neighbor] = current
            g_score[neighbor] = tentative_g_score
            f_score[neighbor] = tentative_g_score + heuristic_cost_estimate(neighbor, goal)
    raise ValueError("Path not found")
