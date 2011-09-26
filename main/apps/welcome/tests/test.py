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
    
    rx_img = re.compile("<img(?P<args>.+?)/?>", re.I | re.M | re.DOTALL)
    rx_attr = re.compile("\s+(?P<name>\S+)\s*=\s*(?P<q>['\"])(?P<value>.+?)(?P=q)")
    
    def test_welcome(self):
        # Anonymous
        status, result = self.get("/")
        self.assertEquals(status, self.HTTP_FORBIDDEN)
        # Authenticated
        status, result = self.get("/", user="test")
        self.assertEquals(status, self.HTTP_OK)
        for match in self.rx_img.finditer(result):
            has_alt = False
            src = None
            for m in self.rx_attr.finditer(match.group("args")):
                attr = m.group("name").lower()
                if attr == "alt":
                    has_alt = True
                elif attr == "src":
                    src = m.group("value")
            self.assertTrue(has_alt and src, "Malformed IMG tag: %s" % match.group(0))
            self.assertTrue(src.startswith("/main/welcome/img/"),
                            "Loading image outside of applicaiton scope: %s" % src)
            status, result = self.get(src, user="test")
            self.assertEquals(status, self.HTTP_OK)
            self.assertTrue(len(result) > 0, "Empty image: %s" % src)
