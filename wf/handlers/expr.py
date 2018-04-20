# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ExprHandler
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# NOC modules
from base import BaseHandler, ContextVarParameter, ExprParameter


class ExprHandler(BaseHandler):
    """
    Assign `v` to the result of `expr`
    """
    params = {
        "v": ContextVarParameter(),
        "expr": ExprParameter()
    }

    def handler(self, process, node, v, expr):
        v.set(expr)
