# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## search Test
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.test import ApplicationTestCase
from django.utils import simplejson as json

class SearchTestCase(ApplicationTestCase):
    ##
    ## test searches
    ##
    def testSearch(self):
        page=self.app.get(self.base_url,user=self.user)
        form=page.forms["search"]
        for q in ["1","192.168.1.1","test"]:
            form["query"]=q
            form.submit()
            form=form.submit().forms["search"]
