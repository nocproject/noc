from noc.lib.render import render
import os
##
## Report Columns
##
class Column(object):
    def __init__(self,name):
        self.name=name
        
    def render_header(self):
        return "<TH>%s</TH>"%self.name
        
    def render_cell(self,value):
        return "<TD>%s</TD>"%value

##
## Abstract Report
##
class BaseReport(object):
    form_class=None # Or forms.form descendant
    template="main/report.html"
    title="Generic Report"
    requires_cursor=False
    columns=[]
    
    def __init__(self,request,query=None):
        self.request=request
        self.query=query
        if self.form_class:
            if self.query:
                self.form=form_class(query)
            else:
                self.form=form_class()
        else:
            self.form=None
        if self.requires_cursor:
            from django.db import connection
            self.cursor = connection.cursor()
            
    def is_valid(self):
        return self.form is None or self.form.is_valid()
    
    def render(self):
        out="<TABLE BORDER=\"1\">"
        out+="<TR>"+"".join([c.render_header() for c in self.columns])+"</TR>"
        for row in self.get_queryset():
            out+="<TR>"+"".join([c.render_cell(v) for c,v in zip(self.columns,row)])+"</TR>"
        out+="</TABLE>"
        return render(self.request,self.template,{"report":self,"query":self.query,"data":out})
            
    def get_queryset(self):
        return []
        
    def execute(self,sql,args=[]):
        self.cursor.execute(sql,args)
        return self.cursor.fetchall()

# A hash of "module" -> hash of name -> report_class
report_classes={}

#
# Register all reports in modules
#
def register_report_classes(module):
    r_path=os.path.join(module,"reports")
    if not os.path.isdir(r_path):
        return
    if module not in report_classes:
        report_classes[module]={}
    for f in [f for f in os.listdir(os.path.join(module,"reports")) if f.endswith(".py") and f!="__init__.py"]:
        try:
            m=__import__("%s.reports.%s"%(module,f[:-3]),globals(),locals(),["Report"])
            rc=getattr(m,"Report")
        except (ImportError,AttributeError):
            continue
        report_classes[module][f[:-3]]=rc
#
# Returns Report Class or raises KeyError
#
def get_report_class(module,name):
    return report_classes[module][name]