# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ReportApplication implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from application import *
##
##
##
class ReportApplication(Application):
    form=None # django.forms.Form class for report queries
    content_types={
        "text" : "text/plain; charset=utf-8",
        "html" : "text/html; charset=utf-8",
        "csv"  : "text/csv; charser=utf-8",
    }
    ##
    def __init__(self,site):
        super(ReportApplication,self).__init__(site)
        site.reports+=[self]
    ##
    ## Return a list of supported formats
    ##
    def supported_formats(self):
        return [f[7:] for f in dir(self) if f.startswith("report_")]
    ##
    ## Return report results to render
    ## Overriden in subclasses
    ##
    def get_data(self,**kwargs):
        pass
    ##
    ## Returns render report as HTML
    ##
    def report_html(self,result,query):
        pass

    def get_menu(self):
        return "Reports | " + unicode(self.title)
    ##
    ## Render report
    ##
    def view_report(self,request,format="html"):
        query={}
        # Check format is valid for application
        if format not in self.supported_formats():
            return self.response_not_found("Unsupported format '%s'"%format)
        # Display and check form if necessary
        if self.form:
            if request.POST:
                # Process POST request and validate data
                form=self.form(request.POST)
                if form.is_valid():
                    query=form.cleaned_data
            else:
                form=self.form()
            # No POST or error - render form
            if not query:
                return self.render(request,"report_form.html",{"form":form,"app":self,"is_report":True})
        # Build result
        rdata=getattr(self,"report_%s"%format)(**query)
        # Render result
        if format=="html":
            return self.render(request,"report.html",{"data":rdata,"app":self,"is_report":True})
        else:
            return self.render_response(rdata,content_type=self.content_types[format])
    view_report.url=r"^$"
    view_report.url_name="view"
    view_report.access=HasPerm("view")
    view_report.menu=get_menu
