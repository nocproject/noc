# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Force10
## OS:     FTOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="Force10.FTOS"
    supported_schemes=[TELNET,SSH]
    pattern_more="^ ?--More--"
    pattern_unpriveleged_prompt=r"^\S+?>"
    command_disable_pager="terminal length 0"
    command_super="enable"
    command_enter_config="configure terminal"
    command_leave_config="exit"
    command_save_config="write memory"
    pattern_prompt=r"^\S+?#"
    command_submit="\r"
    convert_interface_name=noc.sa.profiles.Profile.convert_interface_name_cisco
    
    def generate_prefix_list(self,name,pl,strict=True):
        suffix=""
        if not strict:
            suffix+=" le 32"
        p="no ip prefix-list %s\n"%name
        p+="ip prefix-list %s\n"%name
        p+="\n".join(["    permit %s%s"%(x,suffix) for x in pl])
        p+="\nexit\n"
        return p
    ##
    ## Compare versions.
    ## Versions are in format
    ## N1.N2[.N3[.N4[L]]]
    ##
    @classmethod
    def cmp_version(cls,v1,v2):
        if "a"<=v1[-1]<="z":
            n1=[int(x) for x in v1[:-1].split(".")]+[v1[-1]]
        else:
            n1=[int(x) for x in v1.split(".")]
        if "a"<=v2[-1]<="z":
            n2=[int(x) for x in v2[:-1].split(".")]+[v2[-1]]
        else:
            n2=[int(x) for x in v2.split(".")]
        l1=len(n1)
        l2=len(n2)
        if l1>l2:
            n2+=[None]*(l1-l2)
        elif l1<l2:
            n1+=[None]*(l2-l1)
        for c1,c2 in zip(n1,n2):
            r=cmp(c1,c2)
            if r!=0:
                return r
        return 0
    

##
## Platform matching helpers
##

## S-series
def SSeries(v):
    return v["platform"].startswith("S")

## C-series
def CSeries(v):
    return v["platform"].startswith("C")

## E-series
def ESeries(v):
    return v["platform"].startswith("E")
