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


class BaseReportColumn(object):
    """
    Base report column class.
    Column is dataseries: ((id1: value1), (id2: value2)) - id - index sorted by asc
    """
    name = None  # ColumnName
    fields = None  # RowFields List
    unknown_value = (None, )  # Fill this if empty value
    builtin_sorted = False  # Column index builtin sorted
    multiple_series = False  # Extract return dict columns dataseries
    # {"Series1_name": dataseries1, "Series2_name": dataseries2}

    def __init__(self, sync_ids=None):
        """

        :param sync_ids:
        """
        self.sync_ids = sync_ids  # Sorted Index list
        self.sync_ids_i = iter(self.sync_ids)
        self._current_id = next(self.sync_ids_i)  # Current id
        self._value = None  #
        self._end_series = False  # Tre

    def _extract(self):
        """
        Generate list of rows. Each row is a list of fields. ("id1", "row1", "row2", "row3", ...)
        :return:
        """
        prev_id = 0
        if self.multiple_series and self.builtin_sorted:
            # return {STREAM_NAME1: iterator1, ....}
            for v in merge(self.extract()):
                yield v
        elif self.multiple_series and not self.builtin_sorted:
            raise NotImplementedError("Multiple series supported onl with builtin sorted")
        elif not self.builtin_sorted:
            # Unsuported builtion sorted.
            for v in sorted(self.extract()):
                yield v
        else:
            # Suported builtion sorted.
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
        for row in self._extract():
            # Row: (row_id, row1, ....)
            row_id, row_value = row[0], row[1:]
            if row_id == self._current_id:
                # @todo Check Duplicate ID
                # If row_id equal current sync_id - set value
                self._value = row_value
            elif row_id < self._current_id:
                # row_id less than sync_id, go to next row
                continue
            elif row_id > self._current_id:
                # row_id more than sync_id, go to next sync_id
                while row_id > self._current_id:
                    # fill row unknown_value
                    self._current_id = next(self.sync_ids_i)
                    yield self.unknown_value
                if row_id == self._current_id:
                    # Match sync_id and row_id = set value
                    self._value = row_value
                else:
                    # Step over current sync_id, set  unknown_value
                    self._value = self.unknown_value
            yield self._value  # return current value
            self._current_id = next(self.sync_ids_i)  # Next sync_id
        self._end_series = True
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
        # @todo use column as dict
        if item == self._current_id:
            return self._value
        return self.unknown_value
        # raise NotImplementedError


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
