# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# ISIS Interfaces *MUST HAVE* ISO AFI
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
=======
##----------------------------------------------------------------------
## ISIS Interfaces *MUST HAVE* ISO AFI
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.cm.validators.clipsobject import CLIPSObjectValidator


class ISISISOValidator(CLIPSObjectValidator):
    TITLE = "ISIS Interfaces *MUST HAVE* ISO AFI"
    DESCRIPTION = """
        ISIS Interfaces must have ISO AFI configured
    """
    TAGS = ["isis", "iso"]
    RULES = """
    (defrule {{RULENAME}}
            (subinterface (admin_status 1) (name ?n)(protocols $? "ISIS" $?))
            (not (subinterface (name ?n) (afi $? "ISO" $?)))
            =>
            (assert
                (error (type "Interface | ISIS Without ISO")
                       (obj ?n)))
    )
    """
