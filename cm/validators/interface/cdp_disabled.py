# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Interface *MUST HAVE* CDP disabled
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
=======
##----------------------------------------------------------------------
## Interface *MUST HAVE* CDP disabled
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.cm.validators.clipsinterface import CLIPSInterfaceValidator


class InterfaceCDPDisabledValidator(CLIPSInterfaceValidator):
    TITLE = "Interface *MUST HAVE* CDP disabled"
    DESCRIPTION = """
        Interface must have CDP disabled
    """
    TAGS = ["admin.status"]
    RULES = """
    (defrule {{RULENAME}}
        (interface (name "{{name}}") (protocols $? "CDP" $?))
        =>
        (assert
            (error (type "Interface | CDP Enabled")
                   (obj "{{name}}")))
    )
    """
