# ----------------------------------------------------------------------
# NodeLoader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.loader.base import BaseLoader
from .base import BaseCDAGNode


class NodeLoader(BaseLoader):
    name = "node"
    base_cls = BaseCDAGNode
    base_path = ("core", "cdag", "node")
    ignored_names = {"base", "loader", "window"}


loader = NodeLoader()
