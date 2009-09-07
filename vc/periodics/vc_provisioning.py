# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## VC Provisioning
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.periodic
import time

TIMEOUT=30
CHECK_TIMEOUT=TIMEOUT/10
class Task(noc.sa.periodic.Task):
    name="vc.vc_provisioning"
    description=""
    
    def execute(self):
        from noc.vc.models import VCDomain
        from noc.sa.models import ReduceTask
        
        tasks=[]
        # Get config
        for vc_domain in VCDomain.objects.filter(enable_provisioning=True):
            # Get VCDomain vcs
            vcs=[{"vlan_id":vc.l1,"name":vc.description} for vc in vc_domain.vc_set.all()]
            # Run Map/Reduce task
            for c in vc_domain.vcdomainprovisioningconfig_set.filter(is_enabled=True):
                    task=ReduceTask.create_task(object_selector=c.selector,
                        reduce_script="VlanProvisioningReport",
                        reduce_script_params=c.id,
                        map_script="sync_vlans",
                        map_script_params={"vlans":vcs,"tagged_ports":c.tagged_ports_list},
                        timeout=TIMEOUT)
                    tasks+=[task]
        # Wait for tasks completion
        while tasks:
            time.sleep(CHECK_TIMEOUT)
            nt=[]
            for t in tasks:
                if t.complete:
                    t.get_result() # Trigger VlanProvisioningReport and delete task
                else:
                    nt+=[t]
                tasks=nt
        return True

