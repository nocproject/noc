# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.ProCurve profile test
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from unittest import TestCase
from noc.sa.profiles.HP.ProCurve import Profile

class HPProCurveTestCase(TestCase):
    def test_cmp_version(self):
        self.assertEqual(Profile.cmp_version("Z.14.04","Z.14.08"),-1)
        self.assertEqual(Profile.cmp_version("Z.14.08","Z.14.04"),1)
        self.assertEqual(Profile.cmp_version("Z.14.08","Z.14.08"),0)
        self.assertEqual(Profile.cmp_version("Z.14.08","Y.11.16"),None)
        self.assertEqual(Profile.cmp_version("Y.10.0","Y.11.16"),-1)
    
