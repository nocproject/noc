# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.lib.render import render
from noc.lib.registry import Registry
from django.conf import settings
from django.http import HttpResponse
import cStringIO,csv

#
admin_media_prefix=settings.ADMIN_MEDIA_PREFIX

##
##
##
class ReportRegistry(Registry):
    name="ReportRegistry"
    subdir="reports"
    classname="Report"
report_registry=ReportRegistry()


##
## Report Columns
## 'format' is a function accepting value and returning valid html code
##
class Column(object):
    def __init__(self,name,align=None,v_align=None,format=None,csv_format=None,summary=None):
        self.name=name
        self.align=align
        self.v_align=v_align
        self.format=format
        self.csv_format=csv_format
        if summary:
            self.summary=AGGREGATE_FUNCTIONS[summary]
        else:
            self.summary=None
        
    def render_header(self):
        return "<TH>%s</TH>"%self.name
    
    def render_cell(self,value,bold=False):
        if value is None:
            value=""
        if self.format:
            value=self.format(value)
        flags=[]
        if self.align:
            flags+=["ALIGN='%s'"%self.align]
        if self.v_align:
            flags+=["VALIGN='%s'"%self.v_align]
        if flags:
            flags=" "+" ".join(flags)
        else:
            flags=""
        if bold:
            return "<TD%s><B>%s</B></TD>"%(flags,value)
        else:
            return "<TD%s>%s</TD>"%(flags,value)
    
    def render_csv_header(self):
        return self.name
    
    def render_csv_cell(self,value,bold=False):
        if value is None:
            return ""
        if self.csv_format:
            value=self.csv_format(value)
        return unicode(value).encode("utf-8")
##
## Boolean field rendered as checkmark
##
class BooleanColumn(Column):
    def render_cell(self,value):
        if value:
            url=admin_media_prefix+"img/admin/icon-yes.gif"
        else:
            url=admin_media_prefix+"img/admin/icon-no.gif"
        return "<TD><IMG SRC='%s' /></TD>"%url
##
## Abstract aggregate function
##
class AggregateFunction(object):
    def __init__(self):
        pass
    ##
    ## Update with new value
    ##
    def update(self,value):
        pass
    ##
    ## Return result
    ##
    def get_result(self):
        return None
##
## SUM
##
class SumFunction(AggregateFunction):
    def __init__(self):
        self.v=0
    def update(self,value):
        if value:
            self.v+=value
    def get_result(self):
        return self.v
##
AGGREGATE_FUNCTIONS={
    "sum" : SumFunction,
}
##
##
##
class ReportBase(type):
    def __new__(cls,name,bases,attrs):
        m=type.__new__(cls,name,bases,attrs)
        report_registry.register(m.name,m)
        return m
##
## Abstract Report
##
class Report(object):
    __metaclass__=ReportBase
    name=None
    form_class=None # Or forms.form descendant
    template="main/report.html"
    title="Generic Report"
    requires_cursor=False
    columns=[]
    refresh=None # Time to refresh report (in seconds)
    
    def __init__(self,request,query=None,format=None):
        self.request=request
        self.query=query
        self.format=format if format is not None else "html"
        if self.form_class:
            if self.query:
                self.form=self.form_class(query)
            else:
                self.form=self.form_class()
        else:
            self.form=None
        if self.requires_cursor:
            from django.db import connection
            self.cursor = connection.cursor()
        self.has_summary=len([c for c in self.columns if c.summary])>0
        if self.has_summary:
            self.summary=[]
            for c in self.columns:
                if c.summary:
                    self.summary+=[c.summary()]
                else:
                    self.summary+=[None]
            
    def is_valid(self):
        return self.form is None or self.form.is_valid()
    
    def render_html(self):
        out="<TABLE SUMMARY='%s'>"%self.title
        out+="<THEAD><TR>"+"".join([c.render_header() for c in self.columns])+"</TR></THEAD>"
        n=0
        for row in self.get_queryset():
            out+="<TR CLASS='row%d'>"%((n%2)+1)+"".join([c.render_cell(v) for c,v in zip(self.columns,row)])+"</TR>"
            if self.has_summary: # Calculate aggregates
                for f,v in zip(self.summary,row):
                    if f:
                        f.update(v)
            n+=1
        if self.has_summary: # Render summary
            out+="<TR>"
            for c,s in zip(self.columns,self.summary):
                if s:
                    out+=c.render_cell(s.get_result(),bold=True)
                else:
                    out+="<TD></TD>"
            out+="</TR>"
        out+="</TABLE>"
        out+="<A HREF='?format=csv'><B>CSV Report</B></A>"
        return render(self.request,self.template,{"report":self,"query":self.query,"data":out,"refresh":self.refresh})
    
    def render_csv(self):
        out=cStringIO.StringIO()
        writer=csv.writer(out)
        writer.writerow([c.render_csv_header() for c in self.columns])
        for row in self.get_queryset():
            writer.writerow([c.render_csv_cell(v) for c,v in zip(self.columns,row)])
        return HttpResponse(out.getvalue(),mimetype="text/csv")
    
    def render(self):
        if self.format=="csv":
            return self.render_csv()
        return self.render_html()
        
    def get_queryset(self):
        return []
        
    def execute(self,sql,args=[]):
        self.cursor.execute(sql,args)
        return self.cursor.fetchall()
##
## Matrix report
##
## get_queryset must return a triple of (column-label,row-label,value)
class MatrixReport(Report):
    def render(self):
        data={}
        cl=set()
        rl=set()
        for c,r,v in self.get_queryset():
            data[c,r]=v
            cl.add(c)
            rl.add(r)
        cl=sorted(cl)
        rl=sorted(rl)
        out="<TABLE SUMMARY='%s' BORDER='1'>"%self.title
        out+="<TR><TH></TH>%s</TR>"%"".join(["<TH><DIV CLASS='vtext'>%s</DIV></TH>"%c for c in cl])
        n=0
        for r in rl:
            out+="<TR CLASS='row%d'><TD><B>%s</B></TD>"%((n%2)+1,r)
            for c in cl:
                try:
                    out+="<TD>%s</TD>"%data[c,r]
                except KeyError:
                    out+="<TD>&nbsp;</TD>"
            out+="</TR>"
            n+=1
        out+="</TABLE>"
        return render(self.request,self.template,{"report":self,"query":self.query,"data":out})
