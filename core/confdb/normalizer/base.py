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
from collections import defaultdict
from functools import partial
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

    def get_children(self, token):
        """
        Find children by token
        :param token:
        :return: Node instance or None
        """
        for n in self.children:
            if n.token == token:
                return n
        return None

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
                    break

    def append(self, pattern, handler, matcher=None):
        if pattern:
            token = pattern[0]
            node = self.get_children(token)
            if not node:
                node = Node(token)
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
            for pattern, matcher in f._matcher:
                n.mtree.append(pattern, getattr(n, k), matcher)
            del f._seq
            del f._matcher
        # Process syntax
        if bases[0] == object:
            mcs.parse_syntax(n, SYNTAX)
        elif n.SYNTAX:
            # Apply custom syntax
            mcs.parse_syntax(n, n.SYNTAX)
        return n

    @classmethod
    def parse_syntax(mcs, ncls, syntax):
        for t in syntax:
            mcs.process_token(ncls, t, tuple())

    @classmethod
    def process_token(mcs, ncls, sdef, path):
        path = path + (sdef,)
        if sdef.children:
            for c in sdef.children:
                mcs.process_token(ncls, c, path)
        if sdef.gen:
            mcs.contribute_gen(
                ncls,
                path,
                replace=not sdef.children and sdef.required and not sdef.multi
            )

    @classmethod
    def contribute_gen(mcs, ncls, path, replace=False):
        sdef = path[-1]
        # Check function name is not duplicated
        assert not hasattr(ncls, sdef.gen), "Duplicated generator name: %s" % sdef.gen
        # Generate function
        args = []
        kw = {}
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
        if replace:
            kw["replace"] = True
        if kw:
            r += [str(kw)]
        body = "def %s(self, %s):\n    return %s" % (sdef.gen, ", ".join(args), ", ".join(r))
        ctx = {}
        exec(body, {}, ctx)
        f = ctx[sdef.gen]
        setattr(ncls, sdef.gen, f)


class BaseNormalizer(six.with_metaclass(BaseNormalizerMetaclass, object)):
    # Custom syntax to enrich ConfDB
    SYNTAX = []

    def __init__(self, object, tokenizer):
        self.object = object
        self.tokenizer = tokenizer
        self.deferable_contexts = defaultdict(dict)  # Name -> Context
        self.context = {}
        self.rebase_id = itertools.count()

    def set_context(self, name, value):
        self.context[name] = value

    def get_context(self, name, default=None):
        return self.context.get(name, default)

    def has_context(self, name):
        return name in self.context

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
                    if rt is None:
                        continue  # Unresolved defer
                    if callable(rt):  # Resolved defers
                        for d in rt():
                            yield d
                    else:
                        yield rt

    def defer(self, context, gen=None, **kwargs):
        def yield_resolved():
            for rp in resolved:
                yield rp()

        ctx = self.deferable_contexts[context]
        # Split resolved and deferred variables
        deferables = {}
        nkwargs = {}
        for k in kwargs:
            v = kwargs[k]
            if isinstance(v, tuple):
                dname = v[0]
                if dname in ctx:
                    nkwargs[k] = ctx[dname]
                else:
                    deferables[k] = v[0]
            else:
                nkwargs[k] = v
        # Update context
        if nkwargs:
            ctx.update(nkwargs)
        # Resolve deferables
        resolved = []
        deferred = ctx.get(".", [])
        n_deferred = []
        if nkwargs and deferred:
            # Try to resolve previously deferred functions
            for dg, dk, dv in deferred:
                rv = self._resolve_vars(ctx, dv)
                if rv is not None:
                    dk.update(rv)
                    resolved += [partial(dg, **dk)]
                else:
                    n_deferred += [(dg, dk, dv)]
        if gen and not deferables:
            # Already resolved shortcut
            resolved += [partial(gen, **nkwargs)]
        elif gen and deferables:
            # Add to deferred list
            n_deferred += [(gen, nkwargs, deferables)]
        ctx["."] = n_deferred
        if resolved:
            return yield_resolved
        else:
            return None

    def _resolve_vars(self, ctx, d_map):
        """
        Resolve deferable variables mapping
        :param ctx: Context
        :param d_map: name -> context name mapping
        :return: Dict if fully resolved, None otherwise
        """
        r = {}
        for k in d_map:
            vn = d_map[k]
            if vn in ctx:
                r[k] = ctx[vn]
            else:
                return None
        return r

    def rebase(self, src, dst):
        """
        Mark the part of tree to be rebased to new location

        Usage:
        yield self.rebase(src, dst):

        :param src: Source path
        :param dst: Destination path
        :return:
        """
        def wrap():
            r_id = str(next(self.rebase_id))
            yield ("hints", "rebase", r_id, "from") + src
            yield ("hints", "rebase", r_id, "to") + dst

        return wrap


def match(*args, **kwargs):
    def wrap(f):
        if hasattr(f, "_seq"):
            f._matcher += [(args, kwargs.get("matcher"))]
        else:
            f._seq = next(_match_seq)
            f._matcher = [(args, kwargs.get("matcher"))]
        return f

    return wrap


def deferable(name):
    """
    Denote deferable (i.e. restorable from context, may be later) variable
    :param name: Variable name
    :return:
    """
    return (name,)
