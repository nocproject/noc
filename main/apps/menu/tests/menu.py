# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Test Menu
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.test import ApplicationTestCase
from django.utils import simplejson as json

class MenuTestCase(ApplicationTestCase):
    ##
    ## Test Menu content
    ##
    def testMenu(self):
        # get menu JSON
        page=self.app.get("/main/menu/json/",user=self.user)
        # Check status
        self.assertEqual(page.status_int,200)
        # Check content-type
        self.assertEqual(page.content_type,"text/json")
        # Try to deserialize content
        obj=json.loads(page.body)
        # Check content
        for o in obj:
            assert "app" in o
            assert "title" in o
            assert "items" in o
    ##
    ## Test menu is in default template
    ##
    def testMenuLink(self):
        page=self.app.get("/",user=self.user).follow()
        assert "/main/menu/json" in page

