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
    ## Redirects to the Noc Book
    ##
    def view_nocbook(self,request):
        return self.response_redirect("/static/doc/en/nocbook/html/index.html")
    view_nocbook.url=r"^nocbook/$"
    view_nocbook.url_name="nocbook"
    view_nocbook.menu="Documentation | NOC Book"
    view_nocbook.access=Permit()

    