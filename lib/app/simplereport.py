# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SimpleReport implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from reportapplication import *
import cStringIO,csv
##
##
##
class SimpleReport(ReportApplication):
    ##
    ## Return a hash of
    ## columns -> a list of hashes: {'title','align':...}
    ## data -> a list of data rows 
    ##
    def get_data(self,**kwargs):
        return {
            "header" : "",
            "columns": [],
            "footer" : "",
        }
    ##
    ## Render HTML
    ##
    def render_html(self,data,query):
        # Render header
        s=["<h1>%s</h1>"%self.title]
        if "header" in data:
            s+=[data["header"]]
        # Render table
        if "columns" in data or "data" in data:
            s+=["<table id='report-table' summary='%s'>"%self.title]
            # Render header row
            if "columns" in data:
                s+=["<tr>"]+["<th>%s</th>"%c["title"] for c in data["columns"]]+["</tr>"]
            if "data" in data:
                n=1
                for row in data["data"]:
                    s+=["<tr class='%s'>"%{0:'row1',1:'row2'}[n%2]]
                    for c in row:
                        s+=["<td>%s</td>"%c]
                    s+=["</tr>"]
                    n+=1
            s+=["</table>"]
        # Render footer
        if "footer" in data:
            s+=[data["footer"]]
        return "".join(s)
    ##
    ## Render CSV
    ##
    def render_csv(self,data,query):
        f=cStringIO.StringIO()
        writer=csv.writer(f)
        if "data" in data:
            for row in data["data"]:
                writer.writerow(row)
        return f.getvalue()
