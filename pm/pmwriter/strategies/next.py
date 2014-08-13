## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## *Next* cache drain strategy
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import DrainStrategy


class NextDrainStrategy(DrainStrategy):
    """
    Drain next available item
    """
    name = "next"

    def get_item(self):
        """
        Must yield metric to drain
        """
        return self.cache.iterkeys().next()
