# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Unittests for Activator
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
from noc.lib.test import ModelTestCase
from noc.main.models import *
from noc.sa.interfaces.base import InterfaceTypeError
#
#
#
=======
##----------------------------------------------------------------------
## Unittests for Activator
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.test import ModelTestCase
from noc.main.models import *
from noc.sa.interfaces import InterfaceTypeError
##
##
##
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
class PyRuleTestCase(ModelTestCase):
    model=PyRule

    def test_pyrule(self):
        # Valid version rule
        v_rule=PyRule(name="v_rule",interface="IGetVersion",description="Test Rule",text="""
@pyrule
def get_version():
    return {"vendor":"Cisco","platform":"CBS31X0","version":"12.2(40)EX3"}
""")
        v_rule.save()
        PyRule.call("v_rule")
        # Test InterfaceErrors
        v_rule=PyRule(name="v_rule1",interface="IGetVersion",description="Test Rule",text="""
@pyrule
def get_version():
    return {"vendor":"Cisco","platform":"CBS31X0","ver":"12.2(40)EX3"}
""")
        v_rule.save()
        try:
            PyRule.call("v_rule1")
            raise AssertionError("InterfaceTypeError exception expected")
        except InterfaceTypeError:
            pass
<<<<<<< HEAD


=======
        
        
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
