# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SleepHandler
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# NOC modules
from base import BaseHandler
from noc.sa.interfaces.base import IntParameter


class SleepHandler(BaseHandler):
    """
    Sleep *t* seconds and resume execution
    """
    params = {
        "t": IntParameter()
    }

    def handler(self, process, node, t=1):
        process.sleep(t)
