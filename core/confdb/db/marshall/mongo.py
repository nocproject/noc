# ----------------------------------------------------------------------
# Mongo document marshaller
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ..node import Node
from .base import BaseMarshaller


class MongoMarshaller(BaseMarshaller):
    name = "mongo"

    @classmethod
    def marshall(cls, node):
        def iter_line(n, path):
            if n.children:
                if n.token:
                    n_path = path + [n.token]
                else:
                    n_path = path
                for c in n.iter_nodes():
                    for t in iter_line(c, n_path):
                        yield t
            else:
                yield path + [n.token]

        return {"config": [{"t": x} for x in iter_line(node, [])]}

    @classmethod
    def unmarshall(cls, data):
        node = Node(None)
        for tokens in data["config"]:
            node.insert(tokens)
        return
