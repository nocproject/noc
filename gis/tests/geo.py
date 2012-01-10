# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Geography/Geometry conversion functions
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import NOCTestCase
from noc.gis.geo import *


class GeoTestCase(NOCTestCase):
    def test_tile_size(self):
        "Test tile size is 256"
        self.assertAlmostEquals(TS, 256)

    def test_zero_point(self):
        """
        Test 0, 0 tile index
        """
        for zoom in range(1, 19):
            C = ll_to_xy(zoom, (0, 0))
            self.assertEquals(C, (2 ** (zoom - 1), 2 ** (zoom - 1)))
