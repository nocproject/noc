# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.welcome unittests
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.lib.test import AjaxTestCase


class WelcomeTestCase(AjaxTestCase):
    app = "main.welcome"

    users = {
        "test": {
            "is_superuser": False
        }
    }
    
    def test_welcome(self):
        # Anonymous
        status, result = self.get("/")
        self.assertEquals(status, self.HTTP_FORBIDDEN)
        # Authenticated
        status, result = self.get("/", user="test")
        self.assertEquals(status, self.HTTP_OK)
