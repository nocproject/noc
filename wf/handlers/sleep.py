# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SleepHandler
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# NOC modules
from base import BaseHandler, ExprParameter


class SleepHandler(BaseHandler):
    """
    Sleep *t* seconds and resume execution
    """
    params = {
        "t": ExprParameter()
    }

    def handler(self, process, node, t):
        process.sleep(t)
