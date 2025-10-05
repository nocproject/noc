# ----------------------------------------------------------------------
# Approximate quantiles computation over an unbounded data set
# with low memory and CPU footprints
# See https://www.cs.rutgers.edu/~muthu/bquant.pdf for details
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
import math
from collections import namedtuple, deque
import sys
import threading
from time import perf_counter

# Each sample contains
# * value - sampled item from data stream
# * width - the difference between the lowest possible rank of item i
#           and the lowest possible rank of item i − 1
# * delta - is the difference between the greatest possible rank of item i
#           and the lowest possible rank of item i
Sample = namedtuple("Sample", ["value", "width", "delta"])
MAX_FLOAT = sys.float_info.max


class Stream(object):
    """
    Base class for approximate quantiles compulation

    :param n:
    """

    def __init__(self, buff_size):
        self.buff_size = buff_size
        self.sorted = False
        self.samples = []
        self.merged = []
        self.merged_width = 0

    def f(self, r, n):
        """
        Error function invariant
        :param r: Current rank
        :param n: Total amount of records
        :return: Error function
        """
        raise NotImplementedError

    def _delta(self, r, n):
        return max(int(self.f(r, n)) - 1, 0)

    def insert(self, v):
        """
        Submit value to stream
        :param v:
        :return:
        """
        # Fast unsorted insert untill buffer limit is reached or first query
        self.samples += [Sample(v, 1, 0)]
        self.sorted = False
        if len(self.samples) >= self.buff_size:
            self.flush()

    def _maybe_sort(self):
        """
        Order samples when necessary
        :return:
        """
        if self.sorted:
            return
        self.sorted = True
        self.samples = sorted(self.samples, key=operator.attrgetter("value"))

    def flush(self):
        """
        Flush unmerged samples into merged stream
        :return:
        """
        self._maybe_sort()
        self._merge()
        self.samples = []

    def _merge(self):
        """
        Merge unmerged and merged samples, maintaining merged samples in sorted order
        :return:
        """

        def get_next(iter):
            try:
                return next(iter)
            except StopIteration:
                return None

        def iter_merged():
            # Current estimated rank
            r = 0
            n = len(self.merged)
            # Sampled generator and first item
            sampled_gen = iter(self.samples)
            current_sampled = get_next(sampled_gen)
            # Merged generator and first item
            merged_gen = iter(self.merged)
            current_merged = get_next(merged_gen)
            # Merge loop
            while current_sampled or current_merged:
                if not current_sampled:
                    # Only merged data left, yield rest of merged
                    yield current_merged
                    yield from merged_gen
                    break
                if not current_merged:
                    # Only sampled data left, yield rest of sampled
                    yield Sample(current_sampled.value, 1, self._delta(r, n))
                    n += 1
                    r += 1
                    for current_sampled in sampled_gen:
                        yield Sample(current_sampled.value, 1, self._delta(r, n))
                        n += 1
                        r += 1
                    break
                while current_merged and current_merged.value <= current_sampled.value:
                    yield current_merged
                    r += current_merged.width
                    current_merged = get_next(merged_gen)
                if not current_merged:
                    continue
                while current_sampled and current_sampled.value < current_merged.value:
                    yield Sample(current_sampled.value, 1, self._delta(r, n))
                    n += 1
                    r += 1
                    current_sampled = get_next(sampled_gen)

        def iter_compressed(g):
            c = get_next(g)  # Not None
            x = get_next(g)  # May be None
            dw = 0
            r = 0
            n = len(self.samples) + len(self.merged)
            while x:
                t = self.f(r, n)
                r += c.width
                if c.width + x.width + x.delta <= t:
                    # Merge into next
                    dw += c.width
                    # Reduce n as the sample is skipped and to be merged later
                    n -= 1
                elif dw:
                    # Merge with previous
                    yield Sample(x.value, c.width + x.width + dw, x.delta)
                    dw = 0
                    # Flush stream
                    r += x.width
                    x = get_next(g)
                else:
                    # Uncompressed
                    yield c
                c = x
                x = get_next(g)
            if dw:
                # Merge with previous
                yield Sample(c.value, c.width + dw, c.delta)
            elif c:
                # Uncompressed
                yield c
            if c:
                r += c.width
            self.merged_width = r

        self.merged = list(iter_compressed(iter_merged()))

    def query(self, q):
        """
        Query returns computed q-th percentile value.
        :param q:
        :return:
        """
        assert 0.0 <= q <= 1.0
        if not self.merged:
            # Fast path when not data merged.
            # Provides better accuracy for small sets of data
            ls = len(self.samples)
            if not ls:
                return 0.0
            i = math.ceil(float(ls) * q)
            if i > 0:
                i -= 1
            self._maybe_sort()
            return self.samples[i].value
        # Flush and compact all sampled data
        self.flush()
        # Search through merged data
        r = 0
        t = math.ceil(float(self.merged_width) * q)
        t += math.ceil(self.f(t, len(self.merged)) / 2.0)
        p = None
        for c in self.merged:
            if p:
                r += p.width
                if r + c.width + c.delta > t:
                    return p.value
            p = c
        return 0.0

    def reset(self):
        """
        Reset all data
        :return:
        """
        self.samples = []
        self.merged_width = 0
        self.merged = []
        self.sorted = False


class BiasedStream(Stream):
    """
    Base class for High- and Low-biased quantiles
    where needed quantiles are not known a priori, but
    error guarantees can still be given

    :param n:
    :param epsilon:
    """

    def __init__(self, n, epsilon):
        super().__init__(n)
        self.epsilon = epsilon


class LowBiasedStream(BiasedStream):
    """
    Low-biased quantiles (e.g. 0.01, 0.1, 0.5) where the needed quantiles
    are not knows a priori, but error guarantees can still be given
    even for lower ranks of data distribution.

    The provided epsilon is a relative error, i.e. the true quantile of a value
    returned by a query is guaranteed to be within (1±Epsilon)*Quantile
    """

    def f(self, r, n):
        return 2 * self.epsilon * r


class HighBiasedStream(BiasedStream):
    """
    High-biased quantiles (e.g. 0.01, 0.1, 0.5) where the needed quantiles
    are not knows a priori, but error guarantees can still be given
    even for higher ranks of data distribution.

    The provided epsilon is a relative error, i.e. the true quantile of a value
    returned by a query is guaranteed to be within 1-(1±Epsilon)*(1-Quantile)
    """

    def f(self, r, n):
        return 2 * self.epsilon * (n - r)


class TargetedStream(Stream):
    """
    NewTargeted returns an initialized Stream concerned with a particular set of
    quantile values that are supplied a priori. Knowing these a priori reduces
    space and computation time. The targets map maps the desired quantiles to
    their absolute errors, i.e. the true quantile of a value returned by a query
    is guaranteed to be within (Quantile±Epsilon).

    :param n:
    :param targets: List of (quantile, epsilon)
    """

    def __init__(self, n, targets):
        super().__init__(n)
        self.targets = targets

    def f(self, r, n):
        m = MAX_FLOAT
        for q, eps in self.targets:
            if q * n <= r:
                f = (2.0 * eps * r) / q
            else:
                f = (2.0 * eps * (n - r)) / (1 - q)
            m = min(f, m)
        return m


class Summary(object):
    """
    Group of time-expiring quantiles. Collects up to `n` time slots.
    `Summary` collects quantiles for ttl, 2 * ttl, .. , n * ttl intervals.
    i.e. given `ttl` == 60 and `n` == 5 `Summary` will collects quantiles
    for 1, 2, 3, 4 and 5 minutes intervals.

    :param ttl: Slot time-to live in seconds
    :param n: Amount of slots to collect
    :param kls: `Stream` subclass
    :param *args: `Stream` constructor parameters
    """

    def __init__(self, ttl, n, kls, *args):
        self.ttl = ttl
        self.slots = deque()
        for _ in range(n + 1):
            self.slots.append(kls(*args))
        self.next_shift = None
        self.lock = threading.Lock()

    def register(self, value):
        """
        Register measured `value` to all slots
        :param value: Floating point collecting values
        :return:
        """
        with self.lock:
            self._maybe_rotate()
            for s in self.slots:
                s.insert(value)

    def query(self, q, *args):
        """
        Query quantile for given slots
        :param q: Quantile value
        :param args: List of slot numbers
        :return:
        """
        with self.lock:
            self._maybe_rotate()
            return [self.slots[s + 1].query(q) for s in args]

    def _maybe_rotate(self):
        """
        Rotate and flush slots when necessary
        :return:
        """
        t = perf_counter()
        if not self.next_shift:
            # First call
            self.next_shift = t + self.ttl
            return
        if self.next_shift > t:
            return  # Not expired yet
        delta = t - self.next_shift
        self.next_shift = t + math.ceil(delta / self.ttl) * self.ttl
        to_rotate = min(len(self.slots), math.ceil(delta / self.ttl))
        for _ in range(to_rotate):
            self.slots.appendleft(self.slots.pop())
            self.slots[0].reset()
