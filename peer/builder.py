# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Prefix list builder
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.peer.models import PeeringPoint
from noc.peer.resolver import Resolver
from noc.peer.tree import optimize_prefix_list

PL_THRESHOLD=10

##
## Queries whois database
## and return a list of
## (peering_point,prefix-list-name,prefix-list)
##
def build_prefix_lists():
    pl2pp={}
    f2pl={}
    result=[]
    for pp in PeeringPoint.objects.all():
        for n,f in pp.generated_prefix_lists:
            if n not in pl2pp:
                pl2pp[n]=[pp]
            else:
                pl2pp[n]+=[pp]
            f2pl[f]=n
    r=Resolver().resolve(f2pl.keys())
    for f,v in r.items():
        if f not in f2pl:
            continue
        members,prefix_list=v
        members=list(members)
        members.sort()
        if len(prefix_list)>PL_THRESHOLD:
            prefix_list=optimize_prefix_list(prefix_list)
            strict=False
        else:
            prefix_list=list(prefix_list)
            prefix_list.sort()
            strict=True
        pl_name=f2pl[f]
        for pp in pl2pp[pl_name]:
            profile=pp.profile
            pl=profile.generate_prefix_list(pl_name,prefix_list,strict)
            result+=[(pp,pl_name,pl)]
    return result
            
