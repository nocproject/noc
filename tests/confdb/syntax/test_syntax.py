# ----------------------------------------------------------------------
# Test ConfDB syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import cachetools
import pytest

# NOC modules
from noc.core.confdb.syntax.base import SYNTAX


@cachetools.cached({})
def get_nodes():
    def iter_children(path):
        yield path
        if path[-1].children:
            for c in path[-1].children:
                yield from iter_children((*path, c))

    def iter_nodes():
        for node in SYNTAX:
            yield from iter_children((node,))

    return list(iter_nodes())


def get_path(path):
    def q(n):
        if not isinstance(n.token, type):
            return n.token
        if n.name:
            return f"<{n.name}>"
        return "ANY"

    return " ".join(q(p) for p in path)


@pytest.mark.parametrize("nodes", get_nodes(), ids=get_path)
def test_wildcard_names(nodes) -> None:
    n = nodes[-1]
    if not n.token:
        assert n.name, "Wildcard without name"
