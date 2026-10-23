# ----------------------------------------------------------------------
# indent marshaller
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseMarshaller


class IndentMarshaller(BaseMarshaller):
    name = "indent"

    @classmethod
    def marshall(cls, node):
        def iter_line(n, level):
            if n.token:
                yield f"{'    ' * level}{n.token}"
            if n.children:
                for cn in n.iter_nodes():
                    yield from iter_line(cn, level + 1)

        return "\n".join(iter_line(node, -1))
