# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## INTERFACE: IReduceTask
##----------------------------------------------------------------------
## DESCRIPTION:
## Collect and notify prefix-list provisioning status
##----------------------------------------------------------------------
## PrefixListProvisioningReport
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.peer.models import PrefixListCache

@pyrule
def prefix_list_provisioning(task,peering_point):
    status={True:[],False:[]}
    for mt in task.maptask_set.filter(status="C"):
        r=mt.script_result
        if not r:
            continue
        for tr in r:
            status[tr["status"]]+=[tr["name"]]
    if peering_point.prefix_list_notification_group:
        r=["Provisioned prefix-lists at %s"%peering_point.hostname]
        if status[True]:
            r+=["Success: %s"%", ".join(status[True])]
        if status[False]:
            r+=["Failed: %s"%", ".join(status[True])]
        peering_point.prefix_list_notification_group.notify(subject="Prefix-List provisioning report for %s"%peering_point.hostname,body="\n".join(r))
    # Update PrefixListCache
    now=datetime.datetime.now()
    for name in status[True]:
        try:
            c=PrefixListCache.objects.get(peering_point=peering_point,name=name)
            c.pushed=now
            c.save()
        except PrefixListCache.DoesNotExist:
            continue
