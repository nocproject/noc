# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Interface *MUST BE* administratively up
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
=======
##----------------------------------------------------------------------
## Interface *MUST BE* administratively up
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.cm.validators.clipsobject import CLIPSObjectValidator


class InterfaceDescriptionsValidator(CLIPSObjectValidator):
    TITLE = "All active interfaces *MUST HAVE* descriptions"
    DESCRIPTION = """
        All active interfaces must have descriptions
    """
    TAGS = ["description"]
    RULES = ["""
        (defrule {{RULENAME}}-{{RULENUM}}
            ?i <- (interface (admin_status 1) (description nil) (name ?n))
            =>
            (assert
                (error (type "Interface | No Description")
                       (obj ?n)))
        )
        """,
        """
        (defrule {{RULENAME}}-{{RULENUM}}
            ?i <- (subinterface (admin_status 1) (description nil) (name ?n))
            =>
            (assert
                (error (type "Interface | No Description")
                       (obj ?n)))
        )
        """
    ]
