# ----------------------------------------------------------------------
# JSON marshaller
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import orjson

# NOC modules
from .base import BaseMarshaller
from noc.core.comp import smart_text


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

        return smart_text(orjson.dumps([get_node(x) for x in node.iter_nodes()]))
