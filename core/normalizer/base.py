# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# BaseNormalizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import itertools
# Third-party modules
import six
# NOC modules
from noc.core.ip import IPv4

_match_seq = itertools.count()
ANY = None


class Node(object):
    __slots__ = ["token", "handler", "children", "matcher"]

    def __init__(self, token):
        self.token = token
        self.handler = None
        self.children = []
        self.matcher = None

    def __repr__(self):
        if self.handler:
            return "<Node '%s' (%s)>" % (self.token, self.handler)
        return "<Node '%s'>" % self.token

    def match(self, token):
        return not self.token or token == self.token

    def iter_matched(self, tokens):
        if not tokens and self.handler:
            yield self
        elif tokens:
            for c in self.children:
                if c.match(tokens[0]):
                    for t in c.iter_matched(tokens[1:]):
                        yield t

    def append(self, pattern, handler, matcher=None):
        if pattern:
            node = Node(pattern[0])
            self.children += [node]
            node.append(pattern[1:], handler)
        else:
            self.handler = handler
            self.matcher = matcher


class BaseNormalizerMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        n = type.__new__(mcs, name, bases, attrs)
        n.mtree = Node(None)
        for k in attrs:
            f = attrs[k]
            if not callable(f) or not hasattr(f, "_seq"):
                continue
            n.mtree.append(f._pattern, getattr(n, k), f._matcher)
            del f._seq
            del f._pattern
            del f._matcher
        return n


class BaseNormalizer(six.with_metaclass(BaseNormalizerMetaclass, object)):
    _VR = ("virtual-router", "default", "forwarding-instance", "default")

    def __init__(self, object, tokenizer):
        self.object = object
        self.tokenizer = tokenizer

    def interface_name(self, *args):
        return self.object.profile.get_profile().convert_interface_name(" ".join(args))

    def vr(self, *args):
        """
        Append default virtual router
        :param args:
        :return:
        """
        return self._VR + args

    def to_prefix(self, address, netmask):
        """
        Convert address and netmask to prefix form
        :param address:
        :param netmask:
        :return:
        """
        return IPv4(address, netmask=netmask).prefix

    def __iter__(self):
        for tokens in self.tokenizer:
            for node in self.mtree.iter_matched(tokens):
                # Feed normalized
                for rt in node.handler(self, tokens):
                    yield rt


def match(*args, **kwargs):
    def wrap(f):
        f._seq = next(_match_seq)
        f._pattern = args
        f._matcher = kwargs.get("matcher")
        return f

    return wrap
