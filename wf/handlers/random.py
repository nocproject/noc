# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## RandomHandler
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import random
# NOC modules
from base import BaseHandler
from noc.sa.interfaces.base import Parameter, IntParameter


class AssignHandler(BaseHandler):
    """
    Generate random integer between *min* and *max*
    and place result into *op0*
    """
    params = {
        "op0": Parameter(),
        "min": IntParameter(default=0),
        "max": IntParameter(default=100)
    }

    def handler(self, process, node, op0, min, max):
        r = random.randint(min, max)
        process.update_context_ref(node, "op0", r)
