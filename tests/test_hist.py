# ----------------------------------------------------------------------
# Test noc.core.hist module
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.hist.base import Histogram


@pytest.mark.parametrize(
    ("config", "sample", "expected"),
    [
        # Empty config, all counts to +inf
        ([], [], [0]),
        ([], [1], [1]),
        ([], [1, 2, 3, 4, 5], [5]),
        # One threshold, 1ms
        ([0.001], [], [0, 0]),
        ([0.001], [0], [1, 1]),
        ([0.001], [0, 999], [2, 2]),
        ([0.001], [0, 999, 1000], [3, 3]),
        ([0.001], [0, 999, 1000, 100000], [3, 4]),
        # Two thresholds
        ([0.001, 0.01], [], [0, 0, 0]),
        ([0.001, 0.01], [0], [1, 1, 1]),
        ([0.001, 0.01], [0, 999], [2, 2, 2]),
        ([0.001, 0.01], [0, 999, 1000], [3, 3, 3]),
        ([0.001, 0.01], [0, 999, 1000, 1001], [3, 4, 4]),
        ([0.001, 0.01], [0, 999, 1000, 1001, 5000], [3, 5, 5]),
        ([0.001, 0.01], [0, 999, 1000, 1001, 5000, 9999], [3, 6, 6]),
        ([0.001, 0.01], [0, 999, 1000, 1001, 5000, 9999, 10000], [3, 7, 7]),
        ([0.001, 0.01], [0, 999, 1000, 1001, 5000, 9999, 10000, 100000], [3, 7, 8]),
    ],
)
def test_hist_register(config, sample, expected):
    # Create histogram
    hist = Histogram(config)
    # Fill with samples
    for x in sample:
        hist.register(x)
    # Compare result
    assert hist.get_values() == expected


@pytest.mark.parametrize(
    ("config", "sample", "labels", "expected"),
    [
        # Empty config
        (
            [],
            [],
            {},
            "# TYPE test_bucket untyped\n"
            'test_bucket{le="+Inf"} 0\n'
            "# TYPE test_sum untyped\n"
            "test_sum{} 0.0\n"
            "# TYPE test_count untyped\n"
            "test_count{} 0",
        ),
        (
            [],
            [],
            {"pool": "default"},
            "# TYPE test_bucket untyped\n"
            'test_bucket{pool="default",le="+Inf"} 0\n'
            "# TYPE test_sum untyped\n"
            'test_sum{pool="default"} 0.0\n'
            "# TYPE test_count untyped\n"
            'test_count{pool="default"} 0',
        ),
        # Two thresholds
        (
            [0.001, 0.01],
            [0, 999, 1000, 1001, 5000, 9999, 10000, 100000],
            {},
            "# TYPE test_bucket untyped\n"
            'test_bucket{le="0.001"} 3\n'
            "# TYPE test_bucket untyped\n"
            'test_bucket{le="0.01"} 7\n'
            "# TYPE test_bucket untyped\n"
            'test_bucket{le="+Inf"} 8\n'
            "# TYPE test_sum untyped\n"
            "test_sum{} 0.127999\n"
            "# TYPE test_count untyped\n"
            "test_count{} 8",
        ),
        (
            [0.001, 0.01],
            [0, 999, 1000, 1001, 5000, 9999, 10000, 100000],
            {"pool": "default"},
            "# TYPE test_bucket untyped\n"
            'test_bucket{pool="default",le="0.001"} 3\n'
            "# TYPE test_bucket untyped\n"
            'test_bucket{pool="default",le="0.01"} 7\n'
            "# TYPE test_bucket untyped\n"
            'test_bucket{pool="default",le="+Inf"} 8\n'
            "# TYPE test_sum untyped\n"
            'test_sum{pool="default"} 0.127999\n'
            "# TYPE test_count untyped\n"
            'test_count{pool="default"} 8',
        ),
    ],
)
def test_prom_metrics(config, sample, labels, expected):
    # Create histogram
    hist = Histogram(config)
    # Fill with samples
    for x in sample:
        hist.register(x)
    # Compare result
    metrics = "\n".join(hist.iter_prom_metrics("test", labels))
    assert metrics == expected
