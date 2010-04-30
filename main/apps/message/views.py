# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Display informational messages
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app import Application

class MessageApplication(Application):
    ##
    ## Render success page
    ##
    def view_success(self,request,subject=None,text=None):
        subject=request.GET.get("subject",subject)
        text=request.GET.get("text",text)
        return self.render(request,"success.html",{"subject":subject,"text":text})
    view_success.url=r"^success/$"
    view_success.url_name="success"
    view_success.access=Application.permit_logged
    ##
    ## Render failure page
    ##
    def view_failure(self,request,subject=None,text=None):
        subject=request.GET.get("subject",subject)
        text=request.GET.get("text",text)
        return self.render(request,"failure.html",{"subject":subject,"text":text})
    view_failure.url=r"^failure/$"
    view_failure.url_name="failure"
    view_failure.access=Application.permit_logged
