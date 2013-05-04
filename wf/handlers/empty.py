# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EmptyHandler
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# NOC modules
from base import BaseHandler
from noc.sa.interfaces.base import Parameter


class EmptyHandler(BaseHandler):
    """
    Check op0 is empty
    """
    conditional = True
    params = {
        "op0": Parameter(),
    }

    def handler(self, process, node, op0=None):
        return bool(op0)
