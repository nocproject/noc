# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Spring layout class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import math
# Third-party modules
import networkx as nx
import numpy as np
# NOC modules
from noc.config import config
from .base import LayoutBase


class SpringLayout(LayoutBase):
    # Optimal distance between nodes
    L = config.layout.spring_edge_spacing
    # F-R iterations
    FR_ITERATIONS = config.layout.spring_iterations
    #
    NODE_SIZE = 48

    def get_layout(self):
        G = self.topology.non_isolated_graph()
        # Adjust weights
        for o1, o2 in G.edges:
            G.edges[o1, o2]["weight"] = self.get_weight(
                G.nodes[o1].get("level", self.DEFAULT_LEVEL),
                G.nodes[o2].get("level", self.DEFAULT_LEVEL),
            )
        sf = math.sqrt(len(G))
        # Scale factor, positions will be [0, scale)
        scale = self.L * sf / math.sqrt(2)
        # Normalized distance between nodes
        k = float(self.L) / scale
        min_dist = 2.0 * self.NODE_SIZE / scale
        return fruchterman_reingold_layout(
            G,
            scale=scale,
            k=k,
            iterations=self.FR_ITERATIONS,
            min_dist=min_dist
        )

    @classmethod
    def get_weight(cls, l1, l2):
        return 1
        # return 2 * cls.DEFAULT_LEVEL * (l1 + l2) / cls.L


@nx.utils.random_state(10)
def fruchterman_reingold_layout(G,
                                k=None,
                                pos=None,
                                fixed=None,
                                iterations=50,
                                threshold=1e-4,
                                weight='weight',
                                scale=1,
                                center=None,
                                dim=2,
                                seed=None,
                                min_dist=0.01
                                ):
    """Position nodes using Fruchterman-Reingold force-directed algorithm.
    Parameters
    ----------
    G : NetworkX graph or list of nodes
        A position will be assigned to every node in G.
    k : float (default=None)
        Optimal distance between nodes.  If None the distance is set to
        1/sqrt(n) where n is the number of nodes.  Increase this value
        to move nodes farther apart.
    pos : dict or None  optional (default=None)
        Initial positions for nodes as a dictionary with node as keys
        and values as a coordinate list or tuple.  If None, then use
        random initial positions.
    fixed : list or None  optional (default=None)
        Nodes to keep fixed at initial position.
    iterations : int  optional (default=50)
        Maximum number of iterations taken
    threshold: float optional (default = 1e-4)
        Threshold for relative error in node position changes.
        The iteration stops if the error is below this threshold.
    weight : string or None   optional (default='weight')
        The edge attribute that holds the numerical value used for
        the edge weight.  If None, then all edge weights are 1.
    scale : number (default: 1)
        Scale factor for positions. Not used unless `fixed is None`.
    center : array-like or None
        Coordinate pair around which to center the layout.
        Not used unless `fixed is None`.
    dim : int
        Dimension of layout.
    seed : int, RandomState instance or None  optional (default=None)
        Set the random state for deterministic node layouts.
        If int, `seed` is the seed used by the random number generator,
        if numpy.random.RandomState instance, `seed` is the random
        number generator,
        if None, the random number generator is the RandomState instance used
        by numpy.random.
    Returns
    -------
    pos : dict
        A dictionary of positions keyed by node
    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> pos = nx.spring_layout(G)
    # The same using longer but equivalent function name
    >>> pos = nx.fruchterman_reingold_layout(G)
    """
    if center is None:
        center = np.zeros(dim)
    lg = len(G)
    if not lg:
        return {}
    if lg == 1:
        return {nx.utils.arbitrary_element(G.nodes()): center}

    nfixed = dict(zip(G, range(len(G))))
    if fixed is not None:
        fixed = np.asarray([nfixed[v] for v in fixed])

    if pos is not None:
        # Determine size of existing domain to adjust initial positions
        dom_size = max(coord for pos_tup in pos.values() for coord in pos_tup)
        if dom_size == 0:
            dom_size = 1
        pos_arr = seed.rand(len(G), dim) * dom_size + center

        for i, n in enumerate(G):
            if n in pos:
                pos_arr[i] = np.asarray(pos[n])
    else:
        pos_arr = None

    A = nx.to_numpy_array(G, weight=weight)
    if k is None and fixed is not None:
        # We must adjust k by domain size for layouts not near 1x1
        nnodes, _ = A.shape
        k = dom_size / np.sqrt(nnodes)
    # Cycles
    cycles = [
        [nfixed[x] for x in c]
        for c in nx.cycle_basis(G)
    ]
    #
    pos = _fruchterman_reingold(A, k, pos_arr, fixed, iterations,
                                threshold, dim, seed, min_dist, cycles)
    if fixed is None:
        pos = nx.rescale_layout(pos, scale=scale) + center
    pos = dict(zip(G, pos))
    return pos


def _fruchterman_reingold(A, k=None, pos=None, fixed=None, iterations=50,
                          threshold=1e-4, dim=2, seed=None, min_dist=0.01, cycles=None):
    """
    Position nodes in adjacency matrix A using Fruchterman-Reingold
    """
    try:
        nnodes, _ = A.shape
    except AttributeError:
        msg = "fruchterman_reingold() takes an adjacency matrix as input"
        raise nx.NetworkXError(msg)

    if pos is None:
        # random initial positions
        pos = np.asarray(seed.rand(nnodes, dim), dtype=A.dtype)
    else:
        # make sure positions are of same type as matrix
        pos = pos.astype(A.dtype)

    # optimal distance between nodes
    if k is None:
        k = np.sqrt(1.0 / nnodes)
    # the initial "temperature"  is about .1 of domain area (=1x1)
    # this is the largest step allowed in the dynamics.
    # We need to calculate this in case our fixed positions force our domain
    # to be much bigger than 1x1
    t = max(max(pos.T[0]) - min(pos.T[0]), max(pos.T[1]) - min(pos.T[1])) * 0.1
    # simple cooling scheme.
    # linearly step down by dt on each iteration so last iteration is size dt.
    dt = t / float(iterations + 1)
    # Force weights
    WPF = config.layout.spring_propulsion_force
    WEF = config.layout.spring_edge_force
    WBF = config.layout.spring_bubble_force
    # Weighted coefficients
    WA = WEF * A
    k3 = WPF * (k ** 3)
    # Prepare cycles calculations
    cp = []
    for c in cycles:
        # Optimal bubble radius
        R = k / (math.sin(2.0 * math.pi / len(c)))
        # Indicator array
        iset = set(int(x) for x in c)
        cp += [(R, list(iset), np.array([1.0 if i in iset else 0.0 for i in range(nnodes)]))]
    # the inscrutable (but fast) version
    # this is still O(V^2)
    # could use multilevel methods to speed this up significantly
    for iteration in range(iterations):
        # Apply bubbling force
        if cycles:
            # Resulting bubble displacement force
            bubble_disp = np.zeros((nnodes, dim))
            for R, cind, indicator in cp:
                # Get Center of mass
                com = np.average(pos[cind], axis=0)
                # Get vectors to center of mass
                delta = np.einsum("ij,i->ij", com - pos, indicator)
                # Calculate distances to center of mass
                dist = np.linalg.norm(delta, axis=1)
                # Collect bubble displacement "forces" together
                bubble_disp += np.einsum("ij,i->ij", delta, (dist / R - 1) ** 3)
        # matrix of difference between points
        delta = pos[:, np.newaxis, :] - pos[np.newaxis, :, :]
        # distance between points
        distance = np.linalg.norm(delta, axis=-1)
        # enforce minimum distance of min_dist
        np.clip(distance, min_dist, None, out=distance)
        #
        # displacement "force"
        # Propulsion - reverse cubic
        # Attraction - square against optimal length difference
        displacement = np.einsum('ijk,ij->ik',
                                 delta,
                                 k3 / distance ** 3 - WA * (distance - k) ** 2)
        # Apply bubbling force
        if cycles:
            displacement += WBF * bubble_disp
        # update positions
        length = np.linalg.norm(displacement, axis=-1)
        length = np.where(length < min_dist, min_dist, length)
        delta_pos = np.einsum('ij,i->ij', displacement, t / length)
        if fixed is not None:
            # don't change positions of fixed nodes
            delta_pos[fixed] = 0.0
        pos += delta_pos
        # cool temperature
        t -= dt
        err = np.linalg.norm(delta_pos) / nnodes
        if err < threshold:
            break  # Cold enough, stopping
    return pos
