# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interface *MUST BE* administratively up
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.cm.validators.clipsinterface import CLIPSInterfaceValidator


class InterfaceAdminUpValidator(CLIPSInterfaceValidator):
    TITLE = "Interface *MUST BE* administratively up"
    DESCRIPTION = """
        Interface must be administratively up
    """
    TAGS = ["admin.status"]
    RULES = """
    (defrule {{RULENAME}}
        ?i <- (interface (name "{{name}}") (admin_status 0))
        =>
        (assert
            (error (type "Interface | Admin Status Down")
                   (obj "{{name}}")))
    )
    """
