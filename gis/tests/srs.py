# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# SRS unittests
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.gis.models import SRS
# NOC modules
from noc.lib.test import NOCTestCase


class GeoTestCase(NOCTestCase):
    def test_900913(self):
        self.assertEquals(SRS.objects.filter(srid=900913).count(), 1)
