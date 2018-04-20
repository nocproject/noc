# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# VC Provisioning
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
=======
##----------------------------------------------------------------------
## VC Provisioning
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
"""
"""
import noc.lib.periodic
import time

TIMEOUT=30
CHECK_TIMEOUT=TIMEOUT/10
class Task(noc.lib.periodic.Task):
    name="vc.vc_provisioning"
    description=""
<<<<<<< HEAD

    def execute(self):
        from noc.vc.models.vcdomain import VCDomain
        from noc.sa.models.reducetask import ReduceTask

=======
    
    def execute(self):
        from noc.vc.models import VCDomain
        from noc.sa.models import ReduceTask
        
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        tasks=[]
        # Get config
        for vc_domain in VCDomain.objects.filter(enable_provisioning=True):
            # Get VCDomain vcs
            vcs=[{"vlan_id":vc.l1,"name":vc.name} for vc in vc_domain.vc_set.all()]
            # Run Map/Reduce task
            for c in vc_domain.vcdomainprovisioningconfig_set.filter(is_enabled=True):
                if c.vc_filter:
                    vc_list=[v for v in vcs if c.vc_filter.check(v["vlan_id"])]
                else:
                    vc_list=vcs[:]
                if not vc_list:
                    continue # Refuse to drop all vlans on switches
                task=ReduceTask.create_task(object_selector=c.selector,
                    reduce_script="pyrule:vc_provisioning",
                    reduce_script_params={"config":c},
                    map_script="sync_vlans",
                    map_script_params={"vlans":vc_list,"tagged_ports":c.tagged_ports_list},
                    timeout=TIMEOUT)
                tasks+=[task]
        # Wait for tasks completion
        ReduceTask.wait_for_tasks(tasks)
        return True

