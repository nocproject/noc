# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# PredicateVisitor
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import ast


class PredicateTransformer(ast.NodeTransformer):
    def __init__(self, engine):
        self.engine = engine
        super(PredicateTransformer, self).__init__()

    def visit(self, node):
        # print node, node.__class__.__name__
        return super(PredicateTransformer, self).visit(node)

    def visit_Call(self, node):
        return ast.Call(
            func=ast.Attribute(
                value=ast.Name(id="self", ctx=ast.Load()),
                attr="fn_%s" % node.func.id,
                ctx=ast.Load()
            ),
            args=[ast.Name(id="_input", ctx=ast.Load())] + [self.visit(x) for x in node.args],
            keywords=node.keywords,
            starargs=node.starargs,
            kwargs=node.kwargs
        )

    def visit_BoolOp(self, node):
        def get_call_chain(chain):
            if len(chain) == 1:
                i = ast.Name(id="_input", ctx=ast.Load())
            else:
                i = get_call_chain(chain[1:])
            return ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="self", ctx=ast.Load()),
                    attr="fn_%s" % chain[0].func.id,
                    ctx=ast.Load()
                ),
                args=[i] + [self.visit(x) for x in chain[0].args],
                keywords=chain[0].keywords,
                starargs=chain[0].starargs,
                kwargs=chain[0].kwargs
            )

        if isinstance(node.op, ast.And):
            return get_call_chain(list(reversed(node.values)))
        return node

    def visit_Name(self, node):
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
