# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Test Guides accessibility
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.test import ApplicationTestCase

class DocTestCase(ApplicationTestCase):
    ## Test NOC Book
    def test_nocbook(self):
        page=self.app.get("/main/doc/nocbook/",user=self.user)
        self.assertEqual(page.status_int,302)
        page=page.follow()

