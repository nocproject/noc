# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Test Menu
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.test import ApplicationTestCase
from django.utils import simplejson as json
import types

class MenuTestCase(ApplicationTestCase):
    ##
    ## Test Menu content
    ##
    def test_menu(self):
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
            # Check links
            for title,link in o["items"]:
                if type(link)==types.DictType:
                    assert "items" in link
                    for t,l in link["items"]:
                        self.app.get(l,user=self.user)
                else:
                    self.app.get(link,user=self.user)
    ##
    ## Test menu is in default template
    ##
    def test_menu_link(self):
        page=self.app.get("/",user=self.user).follow()
        assert "/main/menu/json" in page

