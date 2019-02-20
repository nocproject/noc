# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# JSON marshaller
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
import ujson
# NOC modules
from .base import BaseMarshaller


class JSONMarshaller(BaseMarshaller):
    name = "json"

    @classmethod
    def marshall(cls, node):
        def apply_node(r, n):
            rr = {}
            r[n.token] = rr
            for lcn in n.iter_nodes():
                apply_node(rr, lcn)

        result = {}
        for cn in node.iter_nodes():
            apply_node(result, cn)
        return ujson.dumps(result, indent=2)
