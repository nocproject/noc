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

    def visit_Call(self, node, _input=None):
        if not _input:
            _input = ast.Name(id="_input", ctx=ast.Load())
        return ast.Call(
            func=ast.Attribute(
                value=ast.Name(id="self", ctx=ast.Load()),
                attr="fn_%s" % node.func.id,
                ctx=ast.Load()
            ),
            args=[_input] + [self.visit(x) for x in node.args],
            keywords=[ast.keyword(arg=k.arg, value=self.visit(k.value)) for k in node.keywords],
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
