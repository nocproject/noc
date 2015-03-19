# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interface | Shutdown
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from noc.cm.validators.clipsinterface import CLIPSInterfaceValidator


class InterfaceShutdownValidator(CLIPSInterfaceValidator):
    TITLE = "Interface *MUST BE* shutdown"
    DESCRIPTION = """
        Interface must be administratively down
    """
    TAGS = ["shutdown"]
    RULES = """
    (defrule {{RULENAME}}
        ?i <- (interface (name "{{name}}") (admin_status 1))
        =>
        (assert
            (error (name "Interface | Shutdown")
                   (obj "{{name}}")))
    )
    """
