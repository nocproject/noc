# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ip.sync_macs periodic task
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.lib.periodic
import bisect

def sync_macs_reduce(task,addresses):
    from noc.main.models import SystemNotification
    m=dict([(a.address,a) for a in addresses])
    inserted=[]
    updated=[]
    ip_macs={}
    # Syncronize MACs
    for mt in task.maptask_set.filter(status="C"):
        for arp in mt.script_result:
            ip=arp["ip"]
            mac=arp["mac"]
            if ip in m:
                a=m[ip]
                if a.mac!=mac:
                    if a.mac:
                        updated+=[(ip,a.mac,mac)]
                    else:
                        inserted+=[(ip,mac)]
                    a.mac=mac
                    a.save()
                try:
                    ip_macs[ip]+=[(mt.managed_object,mac)]
                except KeyError:
                    ip_macs[ip]=[(mt.managed_object,mac)]
    # Notify
    if inserted or updated:
        s=["MAC Syncronization Report"]
        if inserted:
            s+=["New MACs:"]
            s+=["    %s: %s"%(ip,mac) for ip,mac in inserted]
        if updated:
            s+=["Changed MACs:"]
            s+=["    %s: %s -> %s"%(ip,old_mac,new_mac) for ip,old_mac,new_mac in updated]
        # Search for conflicting MACs
        conflicting=[(ip,M) for ip,M in ip_macs.items() if len(M)>1]
        if conflicting:
            s+=["Conflicting MACs:"]
            for ip,M in conflicting:
                s+=["    %s:"%ip]
                for o,m in M:
                    s+=["        %s: %s"%(o.name,m)]
        SystemNotification.notify("ip.sync_macs",subject="MAC Syncronization Report",body="\n".join(s))


class Task(noc.lib.periodic.Task):
    name="ip.sync_macs"
    description=""
    TIMEOUT=60
    
    def execute(self):
        from noc.sa.models import ReduceTask,ManagedObject
        from noc.ip.models import Address
        
        # Get a list of managed objects to fetch ARP cache
        objects=list(ManagedObject.objects.raw("""
            SELECT DISTINCT a.managed_object_id AS id
            FROM   ip_address a JOIN ip_prefix p ON (a.prefix_id=p.id)
            WHERE
                a.managed_object_id IS NOT NULL
                AND EXISTS (SELECT id FROM ip_address ma WHERE ma.afi='4' AND ma.auto_update_mac AND ma.prefix_id=p.id)
        """))
        # Get a list of addresses to syncronize
        addresses=list(Address.objects.raw("""
            SELECT a.id,a.address,a.mac
            FROM   ip_address a JOIN ip_prefix p ON (a.prefix_id=p.id)
            WHERE
                    a.auto_update_mac
                AND a.afi='4'
                AND EXISTS (SELECT id FROM ip_address oa WHERE oa.prefix_id=p.id AND oa.managed_object_id IS NOT NULL)
        """))
        # Get ARP cache
        task=ReduceTask.create_task(object_selector=objects,
            reduce_script=sync_macs_reduce,
            reduce_script_params={"addresses":addresses},
            map_script="get_arp",
            map_script_params={},
            timeout=self.TIMEOUT)
        # Wait for tasks completion
        ReduceTask.wait_for_tasks([task])
        return True
    
