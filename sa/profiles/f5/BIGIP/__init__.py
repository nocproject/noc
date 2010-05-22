# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: f5
## OS:     BIG-IP
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import SSH

class Profile(noc.sa.profiles.Profile):
    name="f5.BIGIP"
    supported_schemes=[SSH]
    pattern_username="^([Uu]sername|[Ll]ogin):"
    pattern_prompt="bp>"
    pattern_more=[
            (r"^(/var/tmp/shell\.out\.\S+|:)"," "),
            (r"^\(END\) ","q"),
            ]
    def cleaned_input(self,input):
        input=input.replace("\x1b[24;1H\x1b[K","\n")
        return super(Profile,self).cleaned_input(input)
