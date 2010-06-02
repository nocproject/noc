# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Links to the documentation
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app import Application,Permit

##
class DocApplication(Application):
    ##
    ## Redirects to the Administrator's Guide
    ##
    def view_ag(self,request):
        return self.response_redirect("/static/doc/en/ag/html/index.html")
    view_ag.url=r"^ag/$"
    view_ag.url_name="ag"
    view_ag.menu="Documentation | Administrator's Guide"
    view_ag.access=Permit()
    ##
    ## Redirects to the User's Guide
    ##
    def view_ug(self,request):
        return self.response_redirect("/static/doc/en/ug/html/index.html")
    view_ug.url=r"^ug/$"
    view_ug.url_name="ug"
    view_ug.menu="Documentation | User's Guide"
    view_ug.access=Permit()

    