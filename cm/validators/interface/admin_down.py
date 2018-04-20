# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Interface *MUST BE* administratively down
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
=======
##----------------------------------------------------------------------
## Interface *MUST BE* administratively down
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
