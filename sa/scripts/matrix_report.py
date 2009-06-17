# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MatrixReport
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.sa.scripts import ReduceScript as ReduceScriptBase
from noc.lib.svg import vertical_text_inline
import types
##
##
##
class ReduceScript(ReduceScriptBase):
    name="MatrixReport"
    @classmethod
    def execute(cls,task,**kwargs):
        def column_label_svg(s):
            return vertical_text_inline(s)
        def column_label_html(s):
            return "<BR/>".join(s)
        column_label=column_label_svg
        data={}
        cl={}
        rl={}
        for mt in task.maptask_set.all():
            r=mt.script_result
            if type(r)!=types.DictType: # Only applicable to returned dicts
                data["status",mt.managed_object.name]="Fail"
                rl[mt.managed_object.name]=None
                continue
            for k,v in r.items():
                data[k,mt.managed_object.name]=v
                cl[k]=None
                rl[mt.managed_object.name]=None
            data["status",mt.managed_object.name]="Success"
            rl[mt.managed_object.name]=None
        cl=["status"]+sorted(cl.keys())
        rl=sorted(rl.keys())
        out="<TABLE SUMMARY='' BORDER='1'>"
        out+="<TR VALIGN='bottom'><TH></TH>%s</TR>"%"".join(["<TH>%s</TH>"%column_label(c) for c in cl])
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
        return out
