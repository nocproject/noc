# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Display main index page
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
import django.contrib.auth
from noc.lib.app import Application,PermitLogged

class IndexApplication(Application):
    title="Index"
    ##
    ## Display main index page
    ##
    def view_index(self,request):
        return self.render(request,"index.html")
    view_index.url=r"^$"
    view_index.url_name="home"
    view_index.access=PermitLogged()
