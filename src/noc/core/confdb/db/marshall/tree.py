# ----------------------------------------------------------------------
# Tree marshaller
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseMarshaller


class TreeMarshaller(BaseMarshaller):
    name = "tree"

    @classmethod
    def marshall(cls, node):
        def iter_node(n, lvl):
            for lcn in reversed(list(n.iter_nodes())):
                yield from iter_node(lcn, lvl + 1)
            if lvl >= 0:
                yield (lvl, n.token)

        # Process nodes in reversed order
        r = []
        mask = None
        for level, token in iter_node(node, -1):
            new_mask = 1 << level
            if mask is None:
                # Last line
                r.insert(0, f"{'  ' * level}+- {token}")
                mask = new_mask
            else:
                mask = (new_mask | mask) & ((1 << (level + 1)) - 1)
                r.insert(
                    0,
                    f"{''.join('| ' if mask & (1 << i) else '  ' for i in range(level))}+- {token}",
                )
        return "\n".join(r)
