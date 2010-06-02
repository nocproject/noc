# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Report Application
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app import Application,Permit
from noc.main.models import report_registry
##
## Report application
##
class ReportAppplication(Application):
    title="Reports"
    ##
    ## Render report index
    ##
    def view_index(self,request):
        r={}
        for cn,c in report_registry.classes.items():
            m,n=cn.split(".",1)
            if m not in r:
                r[m]=[c]
            else:
                r[m].append(c)
        out=[]
        keys=r.keys()
        keys.sort()
        for k in keys:
            v=r[k]
            v.sort(lambda x,y:cmp(x.title,y.title))
            out.append([k,v])
        return self.render(request,"index.html",{"reports":out})
    view_index.url=r"^$"
    view_index.menu="Reports"
    view_index.access=Permit()
    ##
    ## Render report
    ##
    def view_report(self,request,report):
        try:
            rc=report_registry[report]
        except KeyError:
            return self.response_not_found("No report found")
        format=request.GET.get("format","html")
        report=rc(self,request,request.POST,format=format)
        if report.is_valid():
            return report.render()
        else:
            return self.render(request,"form.html",{"report":report})
    view_report.url=r"^(?P<report>\S+)/$"
    view_report.url_name="view"
    view_report.access=Permit()

