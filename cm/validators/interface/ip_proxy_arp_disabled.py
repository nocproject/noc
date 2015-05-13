# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interface *MUST HAVE* ip proxy arp disabled
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.cm.validators.clipssubinterface import CLIPSSubInterfaceValidator


class InterfaceIPProxyArpDisabledValidator(CLIPSSubInterfaceValidator):
    TITLE = "Interface *MUST HAVE* IP proxy arp disabled"
    DESCRIPTION = """
        Interface must have IP proxy arp disabled
    """
    TAGS = []
    RULES = """
    (defrule {{RULENAME}}
        (subinterface
            (name "{{name}}")
            (admin_status 1)
            (afi $? "IPv4" $?)
            (ip_proxy_arp 1)
        )
        =>
        (assert
            (error (type "Interface | IP Proxy ARP Enabled")
                   (obj "{{name}}")))
    )
    """
