# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MPLS Interfaces *MUST HAVE* ISIS
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.cm.validators.clipsobject import CLIPSObjectValidator


class MPLSISISValidator(CLIPSObjectValidator):
    TITLE = "MPLS Interfaces *MUST HAVE* ISIS"
    DESCRIPTION = """
        MPLS Interfaces must have ISIS protocol configured
    """
    TAGS = ["isis", "mpls"]
    RULES = """
    (defrule {{RULENAME}}
            (subinterface (admin_status 1) (name ?n)(afi $? "MPLS" $?))
            (not (subinterface (name ?n) (protocols $? "ISIS" $?)))
            =>
            (assert
                (error (type "Interface | MPLS Without ISIS")
                       (obj ?n)))
    )
    """
