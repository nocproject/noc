# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EqualHandler
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# NOC modules
from base import BaseHandler
from noc.sa.interfaces.base import Parameter


class EqualHandler(BaseHandler):
    """
    Compare *op1* and *op2*
    """
    conditional = True
    params = {
        "op0": Parameter(),
        "op1": Parameter()
    }

    def handler(self, process, node, op0=None, op1=None):
        return str(op0) == str(op1)
