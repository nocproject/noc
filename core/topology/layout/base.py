# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Base layout class
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

class LayoutBase(object):
    def __init__(self, topology):
        self.topology = topology

    def get_layout(self):
        """
        Returns a *pos* dict
        """
        return {}
