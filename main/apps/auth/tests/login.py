# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Test Login/Logout
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.test import ApplicationTestCase

class LoginTestCase(ApplicationTestCase):
    ##
    def testLogin(self):
        # Login as unauthenticated user
        page=self.app.get("/")
        # We must receive 301 to /main/index
        self.assertEquals(page.status_int,301)
        page=page.follow()
        # We must receive 302 to login page
        self.assertEquals(page.status_int,302)
        page=page.follow()
        # We must get login form
        self.assertEquals(page.status_int,200)
        form=page.form
        # Check incorrect login
        form["username"]=self.user
        form["password"]=self.password+self.password
        page=form.submit()
        # We must get login form again
        assert "this_is_the_login_form" in page
        form["username"]=self.user
        form["password"]=self.password
        page=form.submit()
        # We must get
        #assert "this_is_the_login_form" not in page
    ##
    ## Test click on logout
    ##
    def testLogout(self):
        # Get index page
        page=self.app.get("/",user=self.user).follow()
        # Click Logout
        page=page.click("Log out").follow().follow().follow()
        # We must be redirected to login page
        assert "this_is_the_login_form" in page
        
