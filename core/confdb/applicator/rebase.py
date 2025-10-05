# ----------------------------------------------------------------------
# RebaseApplicator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseApplicator


class RebaseApplicator(BaseApplicator):
    """
    Rebase all scheduled tree locations
    """

    def apply(self):
        root = self.confdb.find("hints", "rebase")
        for node in root.iter_nodes():
            self.apply_node(node)

    def apply_node(self, node):
        f = node.find("from")
        if not f:
            return
        t = node.find("to")
        if not t:
            return
        src_path = self.get_path(f)
        dst_path = self.get_path(t)
        self.confdb.rebase(src_path, dst_path)

    def get_path(self, node):
        """
        Get single path to the end
        :param node:
        :return:
        """
        if node.children:
            assert len(node.children) == 1
            n = next(iter(node.children))
            return [n, *self.get_path(node.children[n])]
        return []

    def can_apply(self):
        return bool(self.confdb.find("hints", "rebase"))
