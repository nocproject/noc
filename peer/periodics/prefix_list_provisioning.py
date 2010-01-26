# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## peer.prefix_list_provisioning
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.periodic
import logging
TIMEOUT=2000

class Task(noc.sa.periodic.Task):
    name="peer.prefix_list_provisioning"
    description=""
    wait_for=["cm.prefix_list_pull"]
    def execute(self):
        from noc.peer.models import PrefixListCache
        from noc.sa.models import ManagedObject,ReduceTask
        #
        prefix_lists={} # PeeringPoint -> [prefix_lists]
        # For all out-of-dated prefix lists
        for pc in PrefixListCache.objects.filter(peering_point__enable_prefix_list_provisioning=True):
            if pc.pushed is not None and pc.pushed>pc.changed:
                continue
            if not pc.data:
                continue
            if pc.peering_point not in prefix_lists:
                prefix_lists[pc.peering_point]=[pc]
            else:
                prefix_lists[pc.peering_point]+=[pc]
        # Run Map/Reduce tasks
        tasks=[]
        for peering_point in prefix_lists:
            # Try to find managed object
            try:
                pp=ManagedObject.objects.get(name=peering_point.hostname)
            except ManagedObject.DoesNotExist:
                logging.warning("No managed object for peering point '%s' found"%peering_point.name)
                continue
            task=ReduceTask.create_task(
                object_selector=[pp],
                reduce_script="PrefixListProvisioningReport",
                reduce_script_params=peering_point.id,
                map_script="sync_prefix_lists",
                map_script_params={"changed_prefix_lists":[{"name":pl.name,"strict":pl.strict,"prefix_list":pl.data} for pl in prefix_lists[peering_point]]},
                timeout=TIMEOUT)
            tasks+=[task]
        # Wait for tasks completion
        ReduceTask.wait_for_tasks(tasks)
        return True
