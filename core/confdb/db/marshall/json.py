# ----------------------------------------------------------------------
# JSON marshaller
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import ujson

# NOC modules
from .base import BaseMarshaller


class JSONMarshaller(BaseMarshaller):
    name = "json"

    @classmethod
    def marshall(cls, node):
        def get_node(n):
            children = [get_node(cn) for cn in n.iter_nodes()]
            r = {"node": n.token}
            if children:
                r["children"] = children
            return r

        return ujson.dumps([get_node(x) for x in node.iter_nodes()])
