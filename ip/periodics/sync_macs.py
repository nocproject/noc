# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ip.sync_macs periodic task
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.periodic
from noc.lib.ip import address_to_int
import bisect

def sync_macs_reduce(task,addresses):
    from noc.main.models import SystemNotification
    m=dict([(a.ip,a) for a in addresses])
    inserted=[]
    updated=[]
    ip_macs={}
    # Syncronize MACs
    for mt in task.maptask_set.filter(status="C"):
        r=mt.script_result
        for arp in r:
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

class Task(noc.sa.periodic.Task):
    name="ip.sync_macs"
    description=""
    TIMEOUT=60
    
    def execute(self):
        def add_block(b,blocks):
            blocks+=[(b.vrf.id,b,address_to_int(b.network),address_to_int(b.broadcast))]
        
        def find_block(ip):
            n_ip=address_to_int(ip.ip)
            vrf_id=ip.vrf.id
            for b_vrf_id,block,b_from,b_to in blocks:
                if b_vrf_id==vrf_id and n_ip>=b_from and n_ip<=b_to:
                    return block
        
        from noc.sa.models import ReduceTask
        from noc.ip.models import IPv4Block,IPv4Address
        # Find all managed objects near addresses
        blocks=[] # (vrf,block,from_ip,to_ip)
        objects=set()
        addresses=[]
        for ip in IPv4Address.objects.filter(auto_update_mac=True):
            addresses+=[ip]
            n_ip=address_to_int(ip.ip)
            # Try to find covering block
            b=find_block(ip)
            if not b:
                b=ip.parent
                add_block(b,blocks)
                # Find managed objects in the block
                objects.update(set([a.managed_object for a in b.addresses if a.managed_object is not None]))
        # Get ARP cache
        task=ReduceTask.create_task(object_selector=list(objects),
            reduce_script=sync_macs_reduce,
            reduce_script_params={"addresses":addresses},
            map_script="get_arp",
            map_script_params={},
            timeout=self.TIMEOUT)
        # Wait for tasks completion
        ReduceTask.wait_for_tasks([task])
        return True