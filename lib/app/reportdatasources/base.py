# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# BaseReportDatasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
import heapq


def iterator_to_stream(iterator):
    """Convert an iterator into a stream (None if the iterator is empty)."""
    try:
        return next(iterator), iterator
    except StopIteration:
        return None


def stream_next(stream):
    """Get (next_value, next_stream) from a stream."""
    val, iterator = stream
    return val, iterator_to_stream(iterator)


def merge(iterators):
    """Make a lazy sorted iterator that merges lazy sorted iterators."""
    streams = map(iterator_to_stream, map(iter, iterators))
    heapq.heapify(streams)
    while streams:
        stream = heapq.heappop(streams)
        if stream is not None:
            val, stream = stream_next(stream)
            heapq.heappush(streams, stream)
            yield val


class LongestIter(object):
    """
    c_did = DiscoveryID._get_collection()
    did = c_did.find({"hostname": {"$exists": 1}}, {"object": 1, "hostname": 1}).sort("object")
        # did = DiscoveryID.objects.filter(hostname__exists=True).order_by("object").scalar("object", "hostname").no_cache()
    hostname = LongestIter(did)
    """
    def __init__(self, it):
        self._iterator = it
        self._end_iterator = False
        self._id = 0
        self._value = None
        self._default_value = None

    def __getitem__(self, item):
        if self._end_iterator:
            return self._default_value
        if self._id == item:
            return self._value
        elif self._id < item:
            self._id = item
            next(self, None)
            return self._value
        elif self._id > item:
            # print("Overhead")
            pass
        return self._default_value

    def __iter__(self):
        for val in self._iterator:
            if val["object"] == self._id:
                self._value = val["hostname"]
            elif val["object"] < self._id:
                continue
            elif val["object"] > self._id:
                self._id = val["object"]
                self._value = val["hostname"]
            yield
        self._end_iterator = True


class BaseReportStream(object):
    name = None  # StreamName
    fields = None  # StreamFields List
    unknown_value = None  # Fill empty value
    builtin_sorted = False  # Builtin Sorted stream
    multiple_stream = False

    def __init__(self, sync_ids=None):
        self.sync_ids = sync_ids
        self.sync_ids_i = iter(self.sync_ids)
        self._current_id = next(self.sync_ids_i)
        self._value = None
        self._end_stream = False

    def _extract(self):
        """
        Generate list of rows. Each row is a list of fields. First value - is id
        :return:
        """
        prev_id = 0
        if not self.builtin_sorted:
            for v in sorted(self.extract()):
                yield v
        elif self.multiple_stream:
            # return {STREAM_NAME1: iterator1, ....}
            for v in merge(self.extract()):
                yield v
        else:
            for v in self.extract():
                if v[0] < prev_id:   # Todo
                    print("Detect unordered stream")
                    raise StopIteration
                yield v
                prev_id = v[0]

    def extract(self):
        """
        Generate list of rows. Each row is a list of fields. First value - is id
        :return:
        """
        raise NotImplementedError

    def __iter__(self):
        for val in self._extract():
            val_id, val = val[0], val[1:]
            if val_id == self._current_id:
                # @todo Check Duplicate ID
                self._value = val
            elif val_id < self._current_id:
                continue
            elif val_id > self._current_id:
                while val_id > self._current_id:
                    self._current_id = next(self.sync_ids_i)
                    yield self.unknown_value
                if val_id == self._current_id:
                    self._value = val
                else:
                    self._value = self.unknown_value
            yield self._value
            self._current_id = next(self.sync_ids_i)
        self._end_stream = True
        # @todo Variant:
        # 1. if sync_ids use to filter in _extract - sync_ids and _extract ending together
        # 2. if sync_ids end before _extract ?
        # 3. if _extract end before sync_ids ?
        if self._current_id:
            # If _extract end before sync_ids to one element
            yield self.unknown_value
        # print("Current ID", self._current_id)
        for _ in self.sync_ids_i:
            # raise StopIteration ?
            yield self.unknown_value

    def __getitem__(self, item):
        # @todo
        if item == self._current_id:
            return self._value
        return self.unknown_value
        # raise NotImplementedError
