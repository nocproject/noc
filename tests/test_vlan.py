# ----------------------------------------------------------------------
# Test noc.core.vlan
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.vlan import has_vlan, optimize_filter


@pytest.mark.parametrize(
    ("vlan_filter", "vlan", "result"),
    [
        # Empty filter
        ("", 1, False),
        ("", "1", False),
        # Single vlan
        ("1", 1, True),
        ("1", "1", True),
        ("1", 2, False),
        ("1", "2", False),
        # Single range
        ("10-20", 9, False),
        ("10-20", 10, True),
        ("10-20", "15", True),
        ("10-20", 20, True),
        ("10-20", 21, False),
        # Value + Range
        ("10,20-30", 9, False),
        ("10,20-30", 10, True),
        ("10,20-30", 11, False),
        ("10,20-30", 19, False),
        ("10,20-30", 20, True),
        ("10,20-30", 25, True),
        ("10,20-30", 30, True),
        ("10,20-30", 31, False),
        # Range + Value
        ("10-20,30", 9, False),
        ("10-20,30", 10, True),
        ("10-20,30", 15, True),
        ("10-20,30", 20, True),
        ("10-20,30", 21, False),
        ("10-20,30", 29, False),
        ("10-20,30", 30, True),
        ("10-20,30", 31, False),
        # Mixed
        ("10,20-30,40,50-60", 9, False),
        ("10,20-30,40,50-60", 10, True),
        ("10,20-30,40,50-60", 11, False),
        ("10,20-30,40,50-60", 19, False),
        ("10,20-30,40,50-60", 20, True),
        ("10,20-30,40,50-60", 25, True),
        ("10,20-30,40,50-60", 30, True),
        ("10,20-30,40,50-60", 31, False),
        ("10,20-30,40,50-60", 39, False),
        ("10,20-30,40,50-60", 40, True),
        ("10,20-30,40,50-60", 41, False),
        ("10,20-30,40,50-60", 49, False),
        ("10,20-30,40,50-60", 50, True),
        ("10,20-30,40,50-60", 55, True),
        ("10,20-30,40,50-60", 60, True),
        ("10,20-30,40,50-60", 61, False),
    ],
)
def test_has_vlan(vlan_filter, vlan, result):
    assert has_vlan(vlan_filter, vlan) is result


@pytest.mark.parametrize(
    ("vlan_filter", "result"),
    [
        # Empty filter
        ("", ""),
        (" ", ""),
        # Single value
        ("1", "1"),
        (" 1", "1"),
        # Sparse single values
        ("1,3", "1,3"),
        ("1, 3", "1,3"),
        # Sparse out-of-order values
        ("3,1", "1,3"),
        # Sparse ranges
        ("1,5-7,10,15-20", "1,5-7,10,15-20"),
        # Sparse out-of-order ranges
        ("1,5-7,15-20,10", "1,5-7,10,15-20"),
        # Single deduplication
        ("1,7,5,3,5", "1,3,5,7"),
        # Single-to-range
        ("1,2,3", "1-3"),
        ("1,3,2,4", "1-4"),
        # Merge ranges
        ("5,7,8-10,10-20", "5,7-20"),
        # Nested ranges
        ("1,5-10,4,3-20,40", "1,3-20,40"),
    ],
)
def test_optimize_filter(vlan_filter, result):
    assert optimize_filter(vlan_filter) == result
