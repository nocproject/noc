# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AddHandler
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# NOC modules
from base import BaseHandler
from noc.sa.interfaces.base import IntParameter, FloatParameter


class AddHandler(BaseHandler):
    """
    Add *op0* and *op1* and store result back in *op0*
    """
    params = {
        "op0": IntParameter() | FloatParameter(),
        "op1": IntParameter() | FloatParameter()
    }

    def handler(self, process, node, op0, op1):
        process.update_context_ref(node, "op0", op0 + op1)
