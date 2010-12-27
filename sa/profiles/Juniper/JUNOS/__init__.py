# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Juniper
## OS:     JUNOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="Juniper.JUNOS"
    supported_schemes=[TELNET,SSH]
    pattern_prompt=r"^(({master}\n)?\S+>)|(({master})?\[edit.*?\]\n\S+#)|(\[Type \^D at a new line to end input\])"
    pattern_more=r"^---\(more.*?\)---"
    command_more=" "
    command_disable_pager="set cli screen-length 0"
    command_enter_config="configure"
    command_leave_config="commit and-quit"
    ##
    ## version comparison
    ## version format:
    ## <major>.<minor>R<h>.<l>
    ##
    def cmp_version(self, x, y):
        def c(v):
            v=v.upper()
            l, r=v.split("R")
            return [int(x) for x in l.split(".")]+[int(x) for x in r.split(".")]
        
        return cmp(c(x), c(y))
    
    ##
    ## prefix-list generator
    ##
    def generate_prefix_list(self,name,pl,strict=True):
        """
        >>> Profile().generate_prefix_list("test",["192.168.0.0/24","192.168.1.0/24"])
        'term pass {\\n    from {\\n        route-filter 192.168.0.0/24 exact;\\n        route-filter 192.168.1.0/24 exact;\\n    }\\n    then next policy;\\n}\\nterm reject {\\n    then reject;\\n}'
        >>> Profile().generate_prefix_list("test",["192.168.0.0/24","192.168.1.0/24"],strict=False)
        'term pass {\\n    from {\\n        route-filter 192.168.0.0/24 orlonger;\\n        route-filter 192.168.1.0/24 orlonger;\\n    }\\n    then next policy;\\n}\\nterm reject {\\n    then reject;\\n}'
        """
        if strict:
            p="        route-filter %s exact;"
        else:
            p="        route-filter %s orlonger;"
        out=["term pass {","    from {"]+[p%x for x in pl]+["    }","    then next policy;","}"]
        out+=["term reject {","    then reject;","}"]
        return "\n".join(out)
