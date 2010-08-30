# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Topology Discovery Application
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app.saapplication import SAApplication
from django import forms
from noc.sa.interfaces import VLANIDParameter,MACAddressParameter
from noc.vc.models import VCDomain
##
## Topolod
##

##
##
##
def reduce_topology(task,mac=True,per_vlan_mac=False,lldp=False):
    from noc.sa.apps.topologydiscovery.topology import TopologyDiscovery
    data=[(mt.managed_object,mt.script_result) for mt in task.maptask_set.filter(status="C")]
    out=["Running topology discovery"]
    td=TopologyDiscovery(data=data,mac=mac,per_vlan_mac=per_vlan_mac,lldp=lldp)
    out+=["Writting topology in /tmp/topo.dot"]
    f=open("/tmp/topo.dot","w")
    f.write(td.dot())
    f.close()
    return "<br/>".join(out)
##
##
##
class TopologyDiscoveryAppplication(SAApplication):
    title="Topology Discovery"
    menu="Tasks | Topology Discovery"
    reduce_task=reduce_topology
    map_task="get_topology_data"
    class TopologyDiscoveryForm(forms.Form):
        mac=forms.BooleanField(label="MAC Address Discovery",initial=True,required=False)
        per_vlan_mac=forms.BooleanField(label="Per-VLAN MAC Discovery",initial=False,required=False)
        lldp=forms.BooleanField(label="LLDP Neighbor Discovery",initial=True,required=False)
    form=TopologyDiscoveryForm
    ##
    ## Prepare map task parameters
    ##
    def clean_map(self,data):
        return {
            "get_mac": "mac" in data and data["mac"],
            "get_lldp": "lldp" in data and data["lldp"]
        }
    ##
    ## Pass form parameters to reduce task
    ##
    def clean_reduce(self,data):
        return data
