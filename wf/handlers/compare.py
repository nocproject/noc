# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## CompareHandler
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# NOC modules
from base import BaseHandler, ExprParameter


class CompareHandler(BaseHandler):
    """
    Process `expr` as boolean expression
    """
    conditional = True
    params = {
        "expr": ExprParameter(),
    }

    def handler(self, process, node, expr):
        return bool(expr)