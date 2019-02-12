# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Tree marshaller
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseMarshaller


class TreeMarshaller(BaseMarshaller):
    name = "tree"

    @classmethod
    def marshall(cls, node):
        def dump_node(n, level):
            lr = []
            if level:
                prefix = "| " * level
            else:
                prefix = ""
            lr += ["%s+- %s" % (prefix, n.token)]
            for lcn in n.iter_nodes():
                lr += dump_node(lcn, level + 1)
            return lr

        r = []
        for cn in node.iter_nodes():
            r += dump_node(cn, 0)
        return "\n".join(r)
