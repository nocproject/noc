# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# BaseNormalizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import itertools
# Third-party modules
import six
# NOC modules
from noc.core.ip import IPv4
from ..patterns import ANY, REST
from ..syntax import SYNTAX

_match_seq = itertools.count()

# Prepare for export
ANY = ANY
REST = REST


class Node(object):
    __slots__ = ["token", "handler", "children", "matcher"]

    def __init__(self, token):
        self.token = token
        self.handler = None
        self.children = []
        self.matcher = None

    def __repr__(self):
        if self.token is None:
            token = "ANY"
        elif self.token is True:
            token = "REST"
        else:
            token = "'%s'" % self.token
        if self.handler:
            return "<Node %s (%s)>" % (token, self.handler.__name__)
        return "<Node %s>" % token

    def match(self, token):
        return self.token is None or self.token is True or token == self.token

    def iter_matched(self, tokens):
        if (not tokens and self.handler) or self.token is True:
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
        # Process matchers
        n.mtree = Node(None)
        for k in attrs:
            f = attrs[k]
            if not callable(f) or not hasattr(f, "_seq"):
                continue
            n.mtree.append(f._pattern, getattr(n, k), f._matcher)
            del f._seq
            del f._pattern
            del f._matcher
        # Process syntax
        if bases[0] == object:
            mcs.parse_syntax(n)
        return n

    @classmethod
    def parse_syntax(mcs, ncls):
        for t in SYNTAX:
            mcs.process_token(ncls, t, tuple())

    @classmethod
    def process_token(mcs, ncls, sdef, path):
        path = path + (sdef,)
        if sdef.children:
            for c in sdef.children:
                mcs.process_token(ncls, c, path)
        if sdef.gen:
            mcs.contribute_gen(ncls, path)

    @classmethod
    def contribute_gen(cls, ncls, path):
        sdef = path[-1]
        # Check function name is not duplicated
        assert not hasattr(ncls, sdef.gen)
        # Generate function
        args = []
        r = []
        for p in path:
            if p.name:
                if p.default:
                    args += ["%s='%s'" % (p.name, p.default.replace("'", "\\'"))]
                else:
                    args += ["%s=None" % p.name]
                r += [p.name]
            else:
                r += ["'%s'" % p.token]
        body = "def %s(self, %s):\n    return %s" % (sdef.gen, ", ".join(args), ", ".join(r))
        ctx = {}
        exec(body, {}, ctx)
        f = ctx[sdef.gen]
        setattr(ncls, sdef.gen, f)


class BaseNormalizer(six.with_metaclass(BaseNormalizerMetaclass, object)):
    def __init__(self, object, tokenizer):
        self.object = object
        self.tokenizer = tokenizer

    def interface_name(self, *args):
        return self.object.profile.get_profile().convert_interface_name(" ".join(args))

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
