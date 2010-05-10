# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## report Test
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.test import ApplicationTestCase
from django.utils import simplejson as json

class reportTestCase(ApplicationTestCase):
    ##
    ## Test invalid report name
    ##
    def test_invalid_report(self):
        page=self.app.get(self.base_url+"XIXARA/",user=self.user,status=[404]) # Invalid report
