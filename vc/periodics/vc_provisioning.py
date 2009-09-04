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
import datetime

class Task(noc.sa.periodic.Task):
    name="vc.vc_provisioning"
    description=""
    
    def execute(self):
        from noc.vc.models import VCDomain
        from noc.sa.models import ReduceTask
        
        # Get config
        for vc_domain in VCDomain.objects.filter(enable_provisioning=True):
            config={} # Selector -> config
            for c in vc_domain.vcdomainprovisioningconfig_set.all():
                if c.selector.name not in config:
                    config[c.selector.name]={"enable":False,"selector":c.selector,"tagged_ports":""}
                config[c.selector.name][c.key]=c.value
            # Normalize values
            for s in config:
                for k in config[s]:
                    v=config[s][k]
                    if k=="enable":
                        config[s][k]=v.lower() in ["t","true","y","yes","1"]
                    elif k=="tagged_ports":
                        config[s][k]=[x.strip() for x in v.split(",")]
            # Get VCDomain vcs
            vcs=[{"vlan_id":vc.l1,"name":vc.description} for vc in vc_domain.vc_set.all()]
            
            # Run Map/Reduce task
            for s in config:
                if config[s]["enable"]:
                    ReduceTask.create_task(object_selector=config[s]["selector"],
                        reduce_script="VLANSyncReport",
                        reduce_script_params=None,
                        map_script="sync_vlans",
                        map_script_params={"vlans":vcs,"tagged_ports":config[s]["tagged_ports"]},
                        timeout=30)
        return True

