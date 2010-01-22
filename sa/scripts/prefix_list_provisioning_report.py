# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PrefixListProvisioningReport
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.sa.scripts import ReduceScript as ReduceScriptBase
import logging,datetime
##
##
class PrefixListProvisioningReport(ReduceScriptBase):
    name="PrefixListProvisioningReport"
    @classmethod
    def execute(cls,task,**kwargs):
        from noc.peer.models import PrefixListCache,PeeringPoint
        pp_id=task.script_params
        try:
            pp=PeeringPoint.objects.get(id=pp_id)
        except PeeringPoint.DoesNotExist:
            logging.error("Peering Point #%d is not found"%pp_id)
            return
        status={True:[],False:[]}
        for mt in task.maptask_set.all():
            r=mt.script_result
            if not r:
                continue
            for tr in r:
                status[tr["status"]]+=[tr["name"]]
        if pp.prefix_list_notification_group:
            r=["Provisioned prefix-lists at %s"%pp.hostname]
            if status[True]:
                r+=["Success: %s"%", ".join(status[True])]
            if status[False]:
                r+=["Failed: %s"%", ".join(status[True])]
            pp.prefix_list_notification_group.notify(subject="Prefix-List provisioning report for %s"%pp.hostname,body="\n".join(r))
        # Update PrefixListCache
        now=datetime.datetime.now()
        for name in status[True]:
            try:
                c=PrefixListCache.objects.get(peering_point=pp,name=name)
                c.pushed=now
                c.save()
            except PrefixListCache.DoesNotExist:
                continue
