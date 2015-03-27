# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interface *MUST HAVE* CDP enabled
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.cm.validators.clipsinterface import CLIPSInterfaceValidator


class InterfaceCDPEnabledValidator(CLIPSInterfaceValidator):
    TITLE = "Interface *MUST HAVE* CDP enabled"
    DESCRIPTION = """
        Interface must have CDP enabled
    """
    TAGS = ["admin.status"]
    RULES = """
    (defrule {{RULENAME}}
        (not (exists (interface (name "{{name}}") (protocols "CDP"))))
        =>
        (assert
            (error (type "Interface | CDP Disabled")
                   (obj "{{name}}")))
    )
    """
