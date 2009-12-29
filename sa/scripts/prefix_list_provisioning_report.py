# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PrefixListProvisioningReport
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.sa.scripts import ReduceScript as ReduceScriptBase
import logging
##
##
class PrefixListProvisioningReport(ReduceScriptBase):
    name="PrefixListProvisioningReport"
    @classmethod
    def execute(cls,task,**kwargs):
        for mt in task.maptask_set.all():
            status={True:[],False:[]}
            r=mt.script_result
            if not r:
                continue
            status[r["status"]]+=[r["name"]]
        pp=PeeringPoint.objects.get(id=task.script_params)
        if pp.prefix_list_notification_group:
            r=["Provisioned prefix-lists at %s"%pp.hostname]
            if status[True]:
                r+=["Success: %s"%", ".join(status[True])]
            if status[False]:
                r+=["Failed: %s"%", ".join(status[True])]
            pp.prefix_list_notification_group.notify(subject="Prefix-List provisioning report for %s"%pp.hostname,body="\n".join(r))
