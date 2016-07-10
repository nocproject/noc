# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## peer.peer application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.peer.models import Peer
from noc.lib.tt import admin_tt_url
from noc.lib.validators import *    
from noc.lib.ip import IP   
from noc.sa.interfaces.base import (ListOfParameter, ModelParameter,
                                    StringParameter)

class PeerApplication(ExtModelApplication):
    """
    Peers application
    """
    title = "Peers"
    menu = "Peers"
    model = Peer
    query_fields = ["remote_asn__icontains","description__icontains",
                    "local_ip__icontains","local_backup_ip__icontains",
                    "remote_ip__icontains","remote_backup_ip__icontains"]

    def clean(self, data):
        data = super(PeerApplication, self).clean(data)
        ## Check address fields
        if not is_prefix(data["local_ip"]):
            raise ValueError("Invalid 'Local IP Address', must be in x.x.x.x/x form or IPv6 prefix")
        if not is_prefix(data["remote_ip"]):         
            raise ValueError("Invalid 'Remote IP Address', must be in x.x.x.x/x form or IPv6 prefix")
        if "local_backup_ip" in data and data["local_backup_ip"]:
            if not is_prefix(data["local_backup_ip"]):
                raise ValueError("Invalid 'Local Backup IP Address', must be in x.x.x.x/x form or IPv6 prefix")
        if "remote_backup_ip" in data and data["remote_backup_ip"]:
            if not is_prefix(data["remote_backup_ip"]):
                raise ValueError("Invalid 'Remote Backup IP Address', must be in x.x.x.x/x form or IPv6 prefix")

        ## Check no or both backup addresses given
        has_local_backup="local_backup_ip" in data and data["local_backup_ip"]
        has_remote_backup="remote_backup_ip" in data and data["remote_backup_ip"]
        if has_local_backup and not has_remote_backup:
            raise ValueError("One of backup addresses given. Set peer address")
        if not has_local_backup and has_remote_backup:
            raise ValueError("One of backup addresses given. Set peer address")
        ## Check all link addresses belongs to one AFI
        if len(set([IP.prefix(data[x]).afi for x in ["local_ip", "remote_ip", "local_backup_ip", "remote_backup_ip"] if x in data and data[x]]))>1:
            raise ValueError("All neighboring addresses must have same address family")
        return data

    ##   
    ## Change peer status
    ##
    def set_peer_status(self,request,queryset,status,message):
        count=0
        for p in queryset:
            p.status=status
            p.save()
            count+=1
        if count==1:
            return "1 peer marked as %s"%message
        else:
            return "%d peers marked as %s"%(count,message)

    @view(url="^actions/planned/$", method=["POST"],
        access="update", api=True,
        validate={
            "ids": ListOfParameter(element=ModelParameter(Peer))
        })

    def api_action_planned(self,request,ids):
        return self.set_peer_status(request,ids,"P","planned")
    api_action_planned.short_description="Mark as planned"

    @view(url="^actions/active/$", method=["POST"],
        access="update", api=True,
        validate={
            "ids": ListOfParameter(element=ModelParameter(Peer))              
        })

    def api_action_active(self,request,ids):
        return self.set_peer_status(request,ids,"A","active")
    api_action_active.short_description="Mark as active"

    @view(url="^actions/shutdown/$", method=["POST"],
        access="update", api=True,
        validate={
            "ids": ListOfParameter(element=ModelParameter(Peer))
        })

    def api_action_shutdown(self,request,ids):
        return self.set_peer_status(request,ids,"S","shutdown")
    api_action_shutdown.short_description="Mark as shutdown"
