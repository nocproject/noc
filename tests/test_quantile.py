# ----------------------------------------------------------------------
# noc.core.quantile tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import time

# Third-party modules
import pytest

# NOC modules
from noc.core.quantile.base import (
    Stream,
    LowBiasedStream,
    HighBiasedStream,
    TargetedStream,
    Summary,
)

# Default quantiles
Q_DEFAULT_EPS = 0.05
Q_DEFAULT_TARGET = [(0.5, 0.01), (0.9, 0.01), (0.95, 0.01)]


# Testing sequences
def seq_empty():
    return iter([])


def seq_const(value, n):
    for _ in range(n):
        yield value


def seq_linear(first, last, n):
    delta = (last - first) / float(n - 1)
    x = first
    for _ in range(n):
        yield x
        x += delta


def test_stream_f():
    stream = Stream(100)
    with pytest.raises(NotImplementedError):
        stream.f(0, 100)


@pytest.mark.parametrize("r,n,expected", [(0, 100, 0.0), (50, 100, 5.0), (100, 100, 10.0)])
def test_low_biased_f(r, n, expected):
    stream = LowBiasedStream(100, Q_DEFAULT_EPS)
    assert stream.f(r, n) == pytest.approx(expected)


@pytest.mark.parametrize("r,n,expected", [(0, 100, 10.0), (50, 100, 5.0), (100, 100, 0.0)])
def test_high_biased_f(r, n, expected):
    stream = HighBiasedStream(100, Q_DEFAULT_EPS)
    assert stream.f(r, n) == pytest.approx(expected)


@pytest.mark.parametrize(
    "r,n,expected",
    [
        (0, 100, 4.0),
        (45, 100, 2.2),
        (50, 100, 2.0),
        (55, 100, 2.2),
        (88, 100, 2.4),
        (90, 100, 2.0),
        (92, 100, 2.044444),
        (94, 100, 2.088889),
        (95, 100, 2.0),
        (96, 100, 2.021053),
        (100, 100, 2.105263),
    ],
)
def test_targeted_f(r, n, expected):
    stream = TargetedStream(100, Q_DEFAULT_TARGET)
    assert stream.f(r, n) == pytest.approx(expected)


def test_targeted_f_extremums():
    stream = TargetedStream(100, Q_DEFAULT_TARGET)
    n = 100
    extremums = set()
    values = list(range(n))
    for r0, r1, r2 in zip(values, values[1:], values[2:]):
        f0 = stream.f(r0, n)
        f1 = stream.f(r1, n)
        f2 = stream.f(r2, n)
        if f1 < f0 and f1 < f2 and f1 != f0 and f1 != f2:
            extremums.add(r1)
    for r, _ in Q_DEFAULT_TARGET:
        assert int(r * n) in extremums
    assert len(extremums) == len(Q_DEFAULT_TARGET)


@pytest.mark.parametrize(
    "seq,expected",
    [
        # Empty samples
        (seq_empty(), [0.0, 0.0, 0.0]),
        # Single sample
        (seq_const(0, 1), [0.0, 0.0, 0.0]),
        (seq_const(1.0, 1), [1.0, 1.0, 1.0]),
        # Test unmerged
        (seq_const(0.0, 50), [0.0, 0.0, 0.0]),
        (seq_const(1.0, 50), [1.0, 1.0, 1.0]),
        (seq_linear(0.0, 1.0, 51), [0.5, 0.9, 0.96]),
        (seq_linear(1.0, 0.0, 51), [0.5, 0.9, 0.96]),
        (seq_const(0.0, 99), [0.0, 0.0, 0.0]),
        (seq_const(1.0, 99), [1.0, 1.0, 1.0]),
        # Test merged
        (seq_const(0.0, 500), [0.0, 0.0, 0.0]),
        (seq_const(1.0, 500), [1.0, 1.0, 1.0]),
        (seq_linear(0.0, 1.0, 501), [0.5, 0.9, 0.95]),
        (seq_linear(1.0, 0.0, 501), [0.5, 0.9, 0.95]),
    ],
)
def test_targeted_quantile(seq, expected):
    stream = TargetedStream(100, Q_DEFAULT_TARGET)
    for sample in seq:
        stream.insert(sample)
    # Query first
    for target, value in zip(stream.targets, expected):
        quantile, epsilon = target
        assert stream.query(quantile) == pytest.approx(value, rel=1e-1)


@pytest.mark.parametrize(
    "seq",
    [
        # Empty
        seq_empty(),
        # Single-value
        seq_const(0.0, 1),
        seq_const(1.0, 1),
        #
        seq_const(0.0, 1000),
        seq_const(1.0, 1000),
        seq_linear(0.0, 1.0, 1000),
        seq_linear(1.0, 0.0, 1000),
    ],
)
def test_low_biased_merged_width(seq):
    stream = LowBiasedStream(100, Q_DEFAULT_EPS)
    n = 0
    for sample in seq:
        stream.insert(sample)
        n += 1
    stream.flush()
    assert stream.merged_width == n


@pytest.mark.parametrize(
    "seq",
    [
        # Empty
        seq_empty(),
        # Single-value
        seq_const(0.0, 1),
        seq_const(1.0, 1),
        #
        seq_const(0.0, 1000),
        seq_const(1.0, 1000),
        seq_linear(0.0, 1.0, 1000),
        seq_linear(1.0, 0.0, 1000),
    ],
)
def test_high_biased_merged_width(seq):
    stream = HighBiasedStream(100, Q_DEFAULT_EPS)
    n = 0
    for sample in seq:
        stream.insert(sample)
        n += 1
    stream.flush()
    assert stream.merged_width == n


@pytest.mark.parametrize(
    "seq",
    [
        # Empty
        seq_empty(),
        # Single-value
        seq_const(0.0, 1),
        seq_const(1.0, 1),
        #
        seq_const(0.0, 1000),
        seq_const(1.0, 1000),
        seq_linear(0.0, 1.0, 1000),
        seq_linear(1.0, 0.0, 1000),
    ],
)
def test_targeted_merged_width(seq):
    stream = TargetedStream(100, Q_DEFAULT_TARGET)
    n = 0
    for sample in seq:
        stream.insert(sample)
        n += 1
    stream.flush()
    assert stream.merged_width == n


def test_reset():
    stream = LowBiasedStream(100, Q_DEFAULT_EPS)
    # Initial
    assert not stream.samples
    assert not stream.merged
    assert not stream.merged_width
    assert not stream.sorted
    # Single value in sampled
    stream.insert(1.0)
    assert len(stream.samples) == 1
    assert not stream.merged
    assert not stream.merged_width
    assert not stream.sorted
    stream.reset()
    assert not stream.samples
    assert not stream.merged
    assert not stream.merged_width
    assert not stream.sorted
    # Single value in merged
    stream.insert(1.0)
    assert len(stream.samples) == 1
    assert not stream.merged
    assert not stream.merged_width
    assert not stream.sorted
    stream.flush()
    assert not stream.samples
    assert len(stream.merged) == 1
    assert stream.merged_width == 1
    assert stream.sorted
    stream.reset()
    assert not stream.samples
    assert not stream.merged
    assert not stream.merged_width
    assert not stream.sorted


def test_summary():
    summary = Summary(1, 3, HighBiasedStream, 100, Q_DEFAULT_EPS)
    # Check slots amount (N+1)
    assert len(summary.slots) == 4
    # Check slots
    for slot in summary.slots:
        assert isinstance(slot, HighBiasedStream)
    # Check insertion
    for v in seq_linear(1.0, 0.0, 10):
        summary.register(v)
        time.sleep(0.5)
    # Request quantiles
    values = summary.query(0.95, 0, 1, 2)
    # Check result. Input sequence is declining, so resulting values must be
    # increasing between time slots
    assert len(values) == 3
    assert values[0] < values[1]
    assert values[1] < values[2]
