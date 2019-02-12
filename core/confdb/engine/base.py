# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Predicate Engine
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import, print_function
import ast
import itertools
import types
# NOC modules
from .transformer import PredicateTransformer
from .var import Var


class Engine(object):
    def __init__(self):
        self.db = None

    def compile(self, expr):
        tree = ast.parse(expr, mode="eval")
        tree = PredicateTransformer(self).visit(tree)
        ast.fix_missing_locations(tree)
        co = compile(tree, "<ast>", "eval")
        return co

    def query(self, expr, **kwargs):
        if not isinstance(expr, types.CodeType):
            expr = self.compile(expr)
        g = eval(expr, {}, {"self": self, "_input": self.iter_initial(**kwargs)})
        for ctx in g:
            yield ctx

    def with_db(self, db):
        self.db = db
        return self

    def iter_product(self, **kwargs):
        if kwargs:
            names = []
            params = []
            for k in kwargs:
                names += [k]
                v = kwargs[k]
                if not isinstance(v, list):
                    v = [v]
                params += [v]
            for values in itertools.product(*params):
                yield dict(zip(names, values))
        else:
            yield {}

    def iter_initial(self, **kwargs):
        for ctx in self.iter_product(**kwargs):
            yield ctx

    def fn_Set(self, _input, **kwargs):
        """
        Set(k1=v1, ..., kN=vN)

        Modify context with additional variables. If v is list, apply all variables product.
        :param _input:
        :param kwargs:
        :return:
        """
        for ctx in _input:
            for pctx in self.iter_product(**kwargs):
                nctx = ctx.copy()
                nctx.update(pctx)
                yield nctx

    def fn_Dump(self, _input, message=None):
        """
        Dump()
        Dump(message)
        Dump current context and pass unmodified
        :param _input:
        :param message:
        :return:
        """
        for ctx in _input:
            if message:
                print("%s: %r" % (message, ctx))
            else:
                print(ctx)
            yield ctx

    def fn_True(self, _input):
        """
        Pass context unmodified
        :param _input:
        :return:
        """
        for ctx in _input:
            yield ctx

    def fn_False(self, _input):
        """
        Break predicate chain
        :param _input:
        :return:
        """
        raise StopIteration

    def fn_Var(self, name):
        """
        Internal function referring to context variable
        :param name:
        :return:
        """
        return Var(name)

    def fn_Sprintf(self, _input, name, fmt, *args):
        """
        :param _input:
        :param name:
        :param fmt:
        :param args:
        :return:
        """
        def resolve(c, v):
            if isinstance(v, Var):
                return v.get(c)
            return v

        assert isinstance(name, Var)
        for ctx in _input:
            nctx = ctx.copy()
            fmt_args = tuple(resolve(nctx, a) for a in args)
            name.set(nctx, fmt % fmt_args)
            yield nctx

    def fn_Match(self, _input, *args):
        def match_token(node, c, current, rest):
            f = node.find(current)
            if f is not None:
                if rest:  # Match tail
                    for wctx in match(f, c, rest):
                        yield wctx
                else:
                    yield c  # Final match

        def match_unbound(node, c, current, rest):
            for f in node.iter_nodes():
                nctx = c.copy()
                nctx[current.name] = f.token
                if rest:
                    for wctx in match(f, nctx, rest):
                        yield wctx
                else:
                    yield nctx

        def match(node, c, where):
            current = where[0]
            rest = where[1:]
            if isinstance(current, Var):
                if current.is_bound(c):
                    for wctx in match_token(node, c, current.get(c), rest):
                        yield wctx
                else:
                    for wctx in match_unbound(node, c, current, rest):
                        yield wctx
            else:
                for wctx in match_token(node, c, current, rest):
                    yield wctx

        assert self.db, "Current database is not set"
        for ctx in _input:
            for nctx in match(self.db.db, ctx, args):
                yield nctx
