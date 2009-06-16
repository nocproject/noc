# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ResultReport
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.sa.scripts import ReduceScript as ReduceScriptBase
import pprint
##
## Returns a table of: managed object, status, pretty-printed result
##
class ReduceScript(ReduceScriptBase):
    name="ResultReport"
    @classmethod
    def execute(cls,task,**kwargs):
        out="<TABLE SUMMARY='' BORDER='1'>"
        out+="<TR><TH>Object</TH><TH>Status</TH><TH>Result</TH></TR>"
        for mt in task.maptask_set.all():
            r=mt.script_result
            out+="<TR><TD>%s</TD><TD>%s</TD><TD><PRE>%s</PRE></TD></TR>"%(mt.managed_object.name,mt.status,pprint.pformat(r))
        out+="</TABLE>"
        return out
