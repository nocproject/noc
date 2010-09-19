# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ResultReport
##----------------------------------------------------------------------
## INTERFACE: IReduceTask
##----------------------------------------------------------------------
## DESCRIPTION:
## Display reduce task result
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
import pprint
##
## Returns a table of: managed object, status, pretty-printed result
##
@pyrule
def result_report(task):
    out=["<table border='1'>","<thead>","<tr><th>Object</th><th>Status</th><th>Result</th></tr>","</thead>","<tbody>"]
    out+=["<TR><TD>%s</TD><TD>%s</TD><TD><PRE>%s</PRE></TD></TR>"%(mt.managed_object.name,mt.status,pprint.pformat(mt.script_result))\
        for mt in task.maptask_set.all()]
    out+=["</tbody>","</table>"]
    return "\n".join(out)
