# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interface *MUST HAVE* CDP disabled
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.cm.validators.clipsinterface import CLIPSInterfaceValidator


class InterfaceCDPDisabledValidator(CLIPSInterfaceValidator):
    TITLE = "Interface *MUST HAVE* CDP disabled"
    DESCRIPTION = """
        Interface must have CDP disabled
    """
    TAGS = ["admin.status"]
    RULES = """
    (defrule {{RULENAME}}
        ?i <- (interface (name "{{name}}") (protocols "CDP"))
        =>
        (assert
            (error (type "Interface | CDP Enabled")
                   (obj "{{name}}")))
    )
    """
