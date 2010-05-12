# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Load Module Names
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from unittest import TestCase
##
## Load MODULE_NAME from __init__.py
##
class LoadModuleNamesTest(TestCase):
    def testNames(self):
        from noc.settings import INSTALLED_APPS
        import noc.settings
        reload(noc.settings)
        for app in INSTALLED_APPS:
            if not app.startswith("noc."):
                continue
            module=__import__(app,{},{},"MODULE_NAME")
            reload(module)
            mn=module.MODULE_NAME
