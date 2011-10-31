# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Force10.FTOS profile test
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from unittest import TestCase
from noc.sa.profiles.Force10.FTOS import *

class Force10FTOSTestCase(TestCase):
    def test_cmp_version(self):
        self.assertEqual(Profile.cmp_version("7.7.1.1","7.7.1.1"),0)
        self.assertEqual(Profile.cmp_version("7.7.1.1","8.3.1.1"),-1)
        self.assertEqual(Profile.cmp_version("8.3.1.1","7.7.1.1"),1)
        self.assertEqual(Profile.cmp_version("8.3.1.3","8.3.1.3d"),-1)
        self.assertEqual(Profile.cmp_version("8.3.1.3d","8.3.1.3e"),-1)
        self.assertEqual(Profile.cmp_version("8.3.1.3e","8.3.1.3"),1)
        self.assertEqual(Profile.cmp_version("8.3.1.3d","8.3.1.5"),-1)
    
    def test_prefix_list(self):
        self.assertEqual(Profile().generate_prefix_list("pl1",
                                                        [("10.0.0.0/8", 8, 8),
                                                         ("192.168.0.0/16", 16, 16)]),
                        'no ip prefix-list pl1\nip prefix-list pl1\n    seq 5 permit 10.0.0.0/8\n    seq 10 permit 192.168.0.0/16\n    exit')
        self.assertEqual(Profile().generate_prefix_list("pl1",
                                                        [("10.0.0.0/8", 8, 8),
                                                         ("192.168.0.0/16", 16, 24)]),
                         'no ip prefix-list pl1\nip prefix-list pl1\n    seq 5 permit 10.0.0.0/8\n    seq 10 permit 192.168.0.0/16 le 24\n    exit')
    
    def test_matchers(self):
        # get_version, E, C, S
        V=[
            [{"vendor":"Force10", "platform": "S50N", "version": "8.2.1.0"}, False, False, True],
            [{"vendor":"Force10", "platform": "S25N", "version": "8.2.1.0"}, False, False, True],
            [{"vendor":"Force10", "platform": "C300", "version": "8.2.1.0"}, False, True, False],
            [{"vendor":"Force10", "platform": "C150", "version": "8.2.1.0"}, False, True, False],
            [{"vendor":"Force10", "platform": "E600i", "version": "8.2.1.0"}, True, False, False],
            [{"vendor":"Force10", "platform": "E1200i", "version": "8.2.1.0"}, True, False, False],
        ]
        
        for v,e,c,s in V:
            self.assertEqual(ESeries(v),e,"E-series check failed for %s"%str(v))
            self.assertEqual(CSeries(v),c,"C-series check failed for %s"%str(v))
            self.assertEqual(SSeries(v),s,"S-series check failed for %s"%str(v))
    
