# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Interface *MUST HAVE* CDP enabled
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
=======
##----------------------------------------------------------------------
## Interface *MUST HAVE* CDP enabled
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.cm.validators.clipsinterface import CLIPSInterfaceValidator


class InterfaceCDPEnabledValidator(CLIPSInterfaceValidator):
    TITLE = "Interface *MUST HAVE* CDP enabled"
    DESCRIPTION = """
        Interface must have CDP enabled
    """
    TAGS = ["admin.status"]
    RULES = """
    (defrule {{RULENAME}}
        (not (exists (interface (name "{{name}}") (protocols $? "CDP" $?))))
        =>
        (assert
            (error (type "Interface | CDP Disabled")
                   (obj "{{name}}")))
    )
    """
