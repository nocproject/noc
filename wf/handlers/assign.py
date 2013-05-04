# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AssignHandler
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# NOC modules
from base import BaseHandler
from noc.sa.interfaces.base import Parameter


class AssignHandler(BaseHandler):
    """
    Assign *op1* to *op2*
    """
    params = {
        "op0": Parameter(),
        "op1": Parameter()
    }

    def handler(self, process, node, op0, op1):
        process.update_context_ref(node, "op0", op1)
