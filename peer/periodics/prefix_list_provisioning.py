# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# peer.prefix_list_provisioning
# flake8: noqa
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
=======
##----------------------------------------------------------------------
## peer.prefix_list_provisioning
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
"""
"""
import noc.lib.periodic
import logging
TIMEOUT=2000

<<<<<<< HEAD

=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
class Task(noc.lib.periodic.Task):
    name="peer.prefix_list_provisioning"
    description=""
    wait_for=["cm.prefix_list_pull"]
    def execute(self):
<<<<<<< HEAD
        from noc.peer.models.prefixlistcache import PrefixListCache
        from noc.sa.models.managedobject import ManagedObject
        from noc.sa.models.reducetask import ReduceTask
=======
        from noc.peer.models import PrefixListCache
        from noc.sa.models import ManagedObject,ReduceTask
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        #
        prefix_lists={} # PeeringPoint -> [prefix_lists]
        # For all out-of-dated prefix lists
        for pc in PrefixListCache.objects.filter():
            if not pc.peering_point.enable_prefix_list_provisioning:
                continue
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
                reduce_script="pyrule:prefix_list_provisioning",
                reduce_script_params={"peering_point":peering_point},
                map_script="sync_prefix_lists",
                map_script_params={"changed_prefix_lists":[{"name":pl.name,"strict":pl.strict,"prefix_list":pl.data} for pl in prefix_lists[peering_point]]},
                timeout=TIMEOUT)
            tasks+=[task]
        # Wait for tasks completion
        ReduceTask.wait_for_tasks(tasks)
        return True
