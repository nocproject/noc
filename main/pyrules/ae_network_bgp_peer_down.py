# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Network | BGP | Peer Down alarm enrichment
##----------------------------------------------------------------------
## INTERFACE: IAlarmEnrichment
##----------------------------------------------------------------------
## DESCRIPTION:
## Enrich alarm with data from peering DB
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.peer.models import Peer


@pyrule
def ae_network_bgp_peer_down(alarm):
    p = Peer.get_peer(alarm.vars["peer"])
    if not p:
        return {}
    else:
        return {
            "local_as": p.local_asn.asn,
            "remote_as": p.remote_asn,
            "local_ip": p.local_ip,
            "remote_ip": p.remote_ip,
            "local_backup_ip": p.local_backup_ip,
            "remote_backup_ip": p.remote_backup_ip,
            "import_filter": p.import_filter,
            "export_filter": p.export_filter,
            "description": p.description
        }
