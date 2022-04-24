# ----------------------------------------------------------------------
# Graph route next hop detection
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Tuple

# Third-party modules
from networkx import shortest_path, NetworkXNoPath
from networkx import Graph
from networkx.classes.graphviews import subgraph_view
from networkx.classes.filters import hide_nodes


def iter_next_hops(G: "Graph", source: str, target: str) -> Tuple[str, int]:
    """
    Yields next hops (direct neighbors of `source` on the possible paths to `target`)
    and shortest path lengths

    :param G: nx.Graph instance
    :param source: Source node
    :param target: Destination node

    :return: Yields (neighbor, path length)
    """
    # Exclude source node from path calculations
    Gv = subgraph_view(G, filter_node=hide_nodes([source]))
    # Calculate shortest path from each neighbors to target
    # Do not allow passing from source
    for hop in G[source]:
        if target == hop:
            yield hop, 2  # Direct next hop
            continue
        try:
            p = shortest_path(Gv, source=hop, target=target)
        except NetworkXNoPath:
            continue
        yield hop, len(p) + 1
