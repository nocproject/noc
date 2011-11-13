# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Unittests for Interfaces and parameters
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import NOCTestCase
from noc.sa.interfaces import *


class ParameterTestCase(NOCTestCase):
    def test_defaults_in_dict(self):
        dp = DictParameter(attrs={
            "a": BooleanParameter(required=True),
            "b": BooleanParameter(default=False, required=True)
        })
        self.assertEqual(
            dp.clean({"a": False, "b": False}),
            {"a": False, "b": False}
        )
        self.assertEqual(
            dp.clean({"a": False}),
            {"a": False, "b": False}
        )
