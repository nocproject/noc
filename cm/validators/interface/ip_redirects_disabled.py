# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interface *MUST HAVE* ip redirects disabled
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.cm.validators.clipssubinterface import CLIPSSubInterfaceValidator


class InterfaceIPProxyArpDisabledValidator(CLIPSSubInterfaceValidator):
    TITLE = "Interface *MUST HAVE* IP redirects disabled"
    DESCRIPTION = """
        Interface must have IP redirects disabled
    """
    TAGS = []
    RULES = """
    (defrule {{RULENAME}}
        (subinterface
            (name "{{name}}")
            (admin_status 1)
            (afi $? "IPv4" $?)
            (ip_redirects 1)
        )
        =>
        (assert
            (error (type "Interface | IP Redirects Enabled")
                   (obj "{{name}}")))
    )
    """
