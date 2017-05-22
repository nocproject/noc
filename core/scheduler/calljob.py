# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Call Job Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from __future__ import absolute_import
from .job import Job
from noc.core.handler import get_handler


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
        self.object = get_handler(self.attrs[self.ATTR_KEY])
        return bool(self.object)
