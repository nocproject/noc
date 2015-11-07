# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Call Job Class
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from job import Job
from noc.lib.solutions import get_solution


class CallJob(Job):
    """
    Delayed job worker.
    Key -- handler name
    args -- handler's kwargs
    """
    name = "call"

    def handler(self, **kwargs):
        self.object(**kwargs)

    def dereference(self):
        self.object = get_solution(self.attrs[self.ATTR_KEY])
        return bool(self.object)
