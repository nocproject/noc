# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Spring layout class
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import math
## Third-party modules
import networkx as nx
## NOC modules
from base import LayoutBase


class SpringLayout(LayoutBase):
    SCALE_FACTOR = 130

    def get_layout(self):
        return nx.spring_layout(
            self.topology.non_isolated_graph(),
            scale=self.SCALE_FACTOR * math.sqrt(len(self.G))
        )
