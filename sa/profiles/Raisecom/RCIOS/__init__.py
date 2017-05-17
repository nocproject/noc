# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Raisecom
## OS:     RCIOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Raisecom.RCIOS"
    pattern_more = "--More-- "
    pattern_username = r"^([Uu]ser ?[Nn]ame|[Ll]ogin): ?"
    pattern_unpriveleged_prompt = r"^(?P<hostname>\S+)> "
    command_super = "enable"
    pattern_prompt = r"^(?P<hostname>\S+)#"
    command_more = " "
    command_exit = "exit"
    pattern_syntax_error = r"% \".+\"  (?:Unknown command.)"

    INTERFACE_TYPES = {
                   "3g": "tunnel",    
                   "du": "loopback",    
                   "et": "physical",  
                   "lo": "loopback",  
                   "sh": "physical",     
                   "si": "physical",
                   "tu": "tunnel",
                   "vl": "SVI",
                   }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get((name[:2]).lower())      