# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Unittests for Activator
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.test import ModelTestCase
from noc.sa.models import *
##
##
##
class ActivatorTestCase(ModelTestCase):
    model=Activator
    fixtures=["activator.json"]
    
    def get_data(self):
        return [
            {"name":"A3","is_active":True,"ip":"10.0.0.1","to_ip":"10.0.0.1"},
            {"name":"A4","is_active":True,"ip":"10.0.0.2","to_ip":"10.0.0.2"}
        ]
    
    #def test_check_ip_access(self):
    #    a1=Activator.objects.get(name="A1")
    #    a2=Activator.objects.get(name="A2")
    #    for ip,r1,r2 in [
    #        ("192.168.0.1", False, False),
    #        ("192.168.0.2", True,  False),
    #        ("192.168.0.3", False, False),
    #        ("192.168.0.255", False, False),
    #        ("192.168.1.0", False, True),
    #        ("192.168.1.128", False, True),
    #        ("192.168.1.255", False, True),
    #        ("192.168.2.0", False, False)
    #        ]:
    #        self.assertEquals(Activator.check_ip_access(ip),r1 or r2)