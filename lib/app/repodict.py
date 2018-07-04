# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ReportDictionary implementation
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging
import heapq
from collections import defaultdict, namedtuple
# Third-party modules
from django.db import connection
from pymongo import ReadPreference
# NOC modules
from noc.lib.nosql import get_db


def iterator_to_stream(iterator):
    """Convert an iterator into a stream (None if the iterator is empty)."""
    try:
        return iterator.next(), iterator
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


class ReportDictionary(object):
    """
    Report Dictionary
    Return dict {id: value} there fill method load(), else unknown method
    Optional Attribute return list Value Name
    """
    UNKNOWN = []
    ATTRS = []

    logger = logging.getLogger(__name__)

    def __init__(self, ids=None, **kwargs):
        self.unknown = self.UNKNOWN
        self.attributes = self.ATTRS
        self.logger.info("Starting load %s", self.ATTRS)
        self.out = self.load(ids or [], self.attributes)
        self.logger.info("Stop loading %s", self.ATTRS)

    @staticmethod
    def load(ids, attributes):
        return {i: [] for i in ids}

    def __getitem__(self, item):
        return self.out.get(item, self.unknown)
