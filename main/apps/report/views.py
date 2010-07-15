# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Report Application
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app import Application,Permit
##
## Report application
##
class ReportAppplication(Application):
    title="Reports"
    ##
    ## Render report index
    ##
    def view_index(self,request):
        # Find available reports
        modules=[] # {title,reports}
        for r in [r for r in self.site.reports if r.view_report.access.check(r,request.user)]:
            if not modules or modules[-1]["title"]!=r.module_title:
                modules+=[{"title":r.module_title,"reports":[r]}]
            else:
                modules[-1]["reports"]+=[r]
        # Sort reports
        for m in modules:
            reports=sorted(m["reports"],lambda x,y:cmp(x.title,y.title))
            m["reports"]=[{
                "title"  : r.title,
                "html"   : self.site.reverse(r.app_id.replace(".",":")+":view","html"),
                "formats": [(f,self.site.reverse(r.app_id.replace(".",":")+":view",f)) for f in r.supported_formats() if f!="html"]
                } for r in reports]
            
        return self.render(request,"index.html",{"modules":modules})
    view_index.url=r"^$"
    view_index.url_name="index"
    view_index.menu="Reports"
    view_index.access=Permit()
