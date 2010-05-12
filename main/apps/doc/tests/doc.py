# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Test Guides accessibility
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.test import ApplicationTestCase

class DocTestCase(ApplicationTestCase):
    ## Test User's Guide
    def testUG(self):
        page=self.app.get("/main/doc/ug/",user=self.user)
        self.assertEqual(page.status_int,302)
        page=page.follow()
    ## Test Administrator's Guide
    def testAG(self):
        page=self.app.get("/main/doc/ag/",user=self.user)
        self.assertEqual(page.status_int,302)
        page=page.follow()

