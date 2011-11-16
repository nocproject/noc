# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Topology Discovery Application
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
## Django modules
from django import forms
## NOC modules
from noc.lib.app.saapplication import SAApplication
from noc.sa.interfaces import VLANIDParameter, MACAddressParameter
from noc.vc.models import VCDomain


def reduce_topology(task, mac=True, per_vlan_mac=False, arp=True, lldp=False,
                    cdp=False, fdp=False,
                    stp=False, save_data=False, mac_port_bindings=False):
    from noc.sa.apps.topologydiscovery.topology import TopologyDiscovery
    import csv

    data = [(mt.managed_object, mt.script_result)
            for mt in task.maptask_set.filter(status="C")]
    # Save raw data when required
    out = ["Running topology discovery"]
    if save_data:
        out += ["Writing raw topology data into /tmp/topo.data"]
        with open("/tmp/topo.data", "w") as f:
            import cPickle

            cPickle.dump(data, f)
    td = TopologyDiscovery(data=data, mac=mac, per_vlan_mac=per_vlan_mac,
                           arp=arp, lldp=lldp, cdp=cdp, fdp=fdp,
                           stp=stp, mac_port_bindings=mac_port_bindings)
    out += ["Writting topology into /tmp/topo.dot"]
    with open("/tmp/topo.dot", "w") as f:
        f.write(unicode(td.dot()).encode("utf-8"))
    if mac_port_bindings:
        out += ["Writing MAC-port bindings into /tmp/mac-port.csv"]
        with open("/tmp/mac-port.csv", "w") as f:
            writer = csv.writer(f)
            for o, i, mac, ip in td.mac_port_bindings:
                writer.writerow([unicode(o).encode("utf-8"), i, mac, ip])
    return "<br/>".join(out)


class TopologyDiscoveryAppplication(SAApplication):
    title = "Topology Discovery"
    menu = "Tasks | Topology Discovery"
    reduce_task = reduce_topology
    map_task = "get_topology_data"

    class TopologyDiscoveryForm(SAApplication.Form):
        mac = forms.BooleanField(label="MAC Address Discovery", initial=True,
                                 required=False)
        per_vlan_mac = forms.BooleanField(label="Per-VLAN MAC Discovery",
                                          initial=False, required=False)
        arp = forms.BooleanField(label="Use ARP cache", initial=True,
                                 required=False)
        lldp = forms.BooleanField(label="LLDP Neighbor Discovery", initial=True,
                                  required=False)
        cdp = forms.BooleanField(label="CDP Neighbor Discovery", initial=False,
                                 required=False)
        fdp = forms.BooleanField(label="FDP Neighbor Discovery", initial=False,
                                 required=False)
        stp = forms.BooleanField(label="STP Discovery", initial=True,
                                 required=False)
        save_data = forms.BooleanField(label="Save Topology Data",
                                       initial=False, required=False)
        mac_port_bindings = forms.BooleanField(label="MAC-Port bindings",
                                               initial=False, required=False)

    form = TopologyDiscoveryForm

    def clean_map(self, data):
        """
         Prepare map task parameters
        :param data:
        :return:
        """
        return {
            "get_mac": "mac"  in data and data["mac"],
            "get_arp": "arp"  in data and data["arp"],
            "get_lldp": "lldp" in data and data["lldp"],
            "get_cdp": "cdp"  in data and data["cdp"],
            "get_fdp": "fdp"  in data and data["fdp"],
            "get_stp": "stp"  in data and data["stp"],
            }

    def clean_reduce(self, data):
        """
        Pass form parameters to reduce task
        :param data:
        :return:
        """
        return data
