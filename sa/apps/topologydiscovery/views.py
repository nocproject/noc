# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Topology Discovery Application
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from __future__ import with_statement
from noc.lib.app.saapplication import SAApplication
from django import forms
from noc.sa.interfaces import VLANIDParameter,MACAddressParameter
from noc.vc.models import VCDomain
##
##
##
def reduce_topology(task,mac=True,per_vlan_mac=False,lldp=False,save_data=False):
    from noc.sa.apps.topologydiscovery.topology import TopologyDiscovery
    data=[(mt.managed_object,mt.script_result) for mt in task.maptask_set.filter(status="C")]
    # Save raw data when required
    out=["Running topology discovery"]
    if save_data:
        out+=["Writing raw topology data into /tmp/topo.data"]
        with open("/tmp/topo.data","w") as f:
            import cPickle
            cPickle.dump(data,f)
    td=TopologyDiscovery(data=data,mac=mac,per_vlan_mac=per_vlan_mac,lldp=lldp)
    out+=["Writting topology into /tmp/topo.dot"]
    with open("/tmp/topo.dot","w") as f:
        f.write(td.dot())
    return "<br/>".join(out)
##
##
##
class TopologyDiscoveryAppplication(SAApplication):
    title="Topology Discovery"
    menu="Tasks | Topology Discovery"
    reduce_task=reduce_topology
    map_task="get_topology_data"
    class TopologyDiscoveryForm(SAApplication.Form):
        mac=forms.BooleanField(label="MAC Address Discovery",initial=True,required=False)
        per_vlan_mac=forms.BooleanField(label="Per-VLAN MAC Discovery",initial=False,required=False)
        lldp=forms.BooleanField(label="LLDP Neighbor Discovery",initial=True,required=False)
        save_data=forms.BooleanField(label="Save Topology Data",initial=False,required=False)
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
