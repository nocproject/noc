# ----------------------------------------------------------------------
# Topology Map loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.topology.base import TopologyBase
from noc.core.loader.base import BaseLoader


class TopologyMapLoader(BaseLoader):
    name = "topology"
    base_cls = TopologyBase
    base_path = ("core", "topology", "map")
    ignored_names = {"loader"}


# Create singleton object
loader = TopologyMapLoader()
