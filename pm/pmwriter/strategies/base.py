## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Base cache drain strategy
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------


class DrainStrategy(object):
    name = "none"

    def __init__(self, cache):
        self.cache = cache

    def get_item(self):
        """
        Must yield metric to drain
        """
        raise NotImplementedError()
