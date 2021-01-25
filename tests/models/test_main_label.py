# ----------------------------------------------------------------------
# main.Label test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Tuple, List

# Third-party modules
import pytest

# NOC modules
from noc.main.models.label import Label


@pytest.mark.parametrize(
    "labels,expected",
    [
        (tuple(), []),
        (([],), []),
        (([], []), []),
        #
        ((["x"],), ["x"]),
        ((["x", "x"],), ["x"]),
        ((["x"], ["x"]), ["x"]),
        ((["x", "y", "x"],), ["x", "y"]),
        ((["x", "y", "x"], ["x"]), ["x", "y"]),
        #
        ((["scope::x"],), ["scope::x"]),
        ((["scope::x", "x"],), ["scope::x", "x"]),
        ((["scope::x", "scope::y"],), ["scope::x"]),
        ((["scope::x", "x", "scope::y"],), ["scope::x", "x"]),
        #
        ((["x", "scope1::scope2::x", "scope1::scope2::x"],), ["x", "scope1::scope2::x"]),
    ],
)
def test_merge_labels(labels: Tuple[List[str]], expected: List[str]):
    assert Label.merge_labels(*labels) == expected
