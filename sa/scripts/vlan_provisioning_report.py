# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## VlanProvisioningReport
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.sa.scripts import ReduceScript as ReduceScriptBase
import logging
##
##
class VlanProvisioningReportn(ReduceScriptBase):
    name="VlanProvisioningReport"
    @classmethod
    def execute(cls,task,**kwargs):
        from noc.vc.models import VCDomainProvisioningConfig
        cfg=VCDomainProvisioningConfig.objects.get(id=task.script_params)
        created={}
        removed={}
        for mt in task.maptask_set.all():
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
        notification_group=cfg.notification_group
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
            notification_group.notify(subject="VLAN Provisioning Report for Domain '%s'"%cfg.vc_domain.name,
                body="\n".join(r))
