# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# PredicateVisitor
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import ast
import itertools

CVAR_NAME = "_ctx"


class PredicateTransformer(ast.NodeTransformer):
    def __init__(self, engine):
        self.engine = engine
        super(PredicateTransformer, self).__init__()

    def wrap_callable(self, node):
        return ast.Lambda(
            args=ast.arguments(
                args=[ast.Name(id=CVAR_NAME, ctx=ast.Param())],
                vararg=None,
                kwarg=None,
                defaults=[]
            ),
            body=node
        )

    def wrap_visitor(self, node):
        return self.visit(node)

    def wrap_expr(self, node):
        return self.wrap_callable(ExpressionTransformer().visit(node))

    def visit_args(self, fn, args):
        if not args:
            return args
        vx = getattr(fn, "visitor", None)
        if not vx:
            return [self.wrap_visitor(x) for x in args]
        wrap = {
            "x": self.wrap_expr,
            "v": self.wrap_visitor
        }
        return [wrap[v](a) for v, a in itertools.izip_longest(vx, args, fillvalue=vx[-1])]

    def visit_Call(self, node, _input=None):
        if not _input:
            _input = ast.Name(id="_input", ctx=ast.Load())
        fn = getattr(self.engine, "fn_%s" % node.func.id)
        return ast.Call(
            func=ast.Attribute(
                value=ast.Name(id="self", ctx=ast.Load()),
                attr="fn_%s" % node.func.id,
                ctx=ast.Load()
            ),
            args=[_input] + self.visit_args(fn, node.args),
            keywords=[ast.keyword(arg=k.arg, value=self.wrap_expr(k.value)) for k in node.keywords],
            starargs=node.starargs,
            kwargs=node.kwargs
        )

    def visit_BoolOp(self, node):
        def get_and_call_chain(chain):
            if len(chain) == 1:
                return self.visit_Call(chain[0])
            return self.visit_Call(chain[0], get_and_call_chain(chain[1:]))

        if isinstance(node.op, ast.And):
            return get_and_call_chain(list(reversed(node.values)))
        return node

    def visit_Name(self, node):
        """
        Convert Name(id=name) to self.fn_Var(name)
        :param node:
        :return:
        """
        return ast.Call(
            func=ast.Attribute(
                value=ast.Name(id="self", ctx=ast.Load()),
                attr="fn_Var",
                ctx=ast.Load()
            ),
            args=[ast.Str(s=node.id)],
            keywords=[],
            starargs=None,
            kwargs=None
        )

    def visit_UnaryOp(self, node):
        if isinstance(node.op, ast.Not):
            return ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="self", ctx=ast.Load()),
                    attr="op_Not",
                    ctx=ast.Load()
                ),
                args=[self.visit(node.operand)],
                keywords=[],
                starargs=None,
                kwargs=None
            )

        return node


class ExpressionTransformer(ast.NodeTransformer):
    RESERVED_NAMES = {"True", "False", "None"}

    def visit_Name(self, node):
        if node.id in self.RESERVED_NAMES:
            return node
        return ast.Subscript(
            value=ast.Name(id=CVAR_NAME, ctx=ast.Load()),
            slice=ast.Index(value=ast.Str(s=node.id)),
            ctx=ast.Load()
        )
