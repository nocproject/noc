# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## refbook Test
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.test import ApplicationTestCase

class RefBookTestCase(ApplicationTestCase):
    fixtures=["refbook.json"]
    
    def test_refbook(self):
        # Ger refbooks list
        index_page=self.app.get(self.base_url,user=self.user)
        # Go to refbook
        view_page=index_page.click("ISO 3166 Country Codes")
        # Search for "Russia"
        form=view_page.forms["changelist-search"]
        form["query"]="RUSSIA"
        view_page=form.submit()
        # Click Russian Federation
        item_page=view_page.click("RUSSIAN FEDERATION")
        # Click "Change"
        change_page=item_page.click("Change",index=1)
        change_page.forms["edit-form"].submit()
