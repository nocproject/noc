# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## vc_provisioning reduce task
##----------------------------------------------------------------------
## INTERFACE: IReduceTask
##----------------------------------------------------------------------
## DESCRIPTION:
## Check sync_vlan completion status
## and notify about changes
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
@pyrule
def vc_provisioning(task,config):
    created={}
    removed={}
    for mt in task.maptask_set.filter(status="C"):
        r=mt.script_result
        if not r:
            continue
        for vlan in r["created"]:
            if vlan not in created:
                created[vlan]=[mt.managed_object.name]
            else:
                created[vlan]+=[mt.managed_object.name]
        for vlan in r["removed"]:
            if vlan not in removed:
                removed[vlan]=[mt.managed_object.name]
            else:
                removed[vlan]+=[mt.managed_object.name]
    notification_group=config.notification_group
    if notification_group and (created or removed):
        r=[]
        if created:
            r+=["Created VLANs"]
            for vlan in sorted(created.keys()):
                r+=["    %d: %s"%(vlan,", ".join([n for n in sorted(created[vlan])]))]
        if removed:
            r+=["Removed VLANs"]
            for vlan in sorted(removed.keys()):
                r+=["    %d: %s"%(vlan,", ".join([n for n in sorted(removed[vlan])]))]
        notification_group.notify(subject="VLAN Provisioning Report for Domain '%s'"%config.vc_domain.name,
            body="\n".join(r))
