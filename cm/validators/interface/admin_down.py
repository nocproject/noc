# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interface *MUST BE* administratively down
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.cm.validators.clipsinterface import CLIPSInterfaceValidator


class InterfaceAdminDownValidator(CLIPSInterfaceValidator):
    TITLE = "Interface *MUST BE* administratively down"
    DESCRIPTION = """
        Interface must be administratively down
    """
    TAGS = ["admin.status"]
    RULES = """
    (defrule {{RULENAME}}
        ?i <- (interface (name "{{name}}") (admin_status 1))
        =>
        (assert
            (error (type "Interface | Admin Status Up")
                   (obj "{{name}}")))
    )
    """
