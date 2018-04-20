# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Service *MUST BE* enabled
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
=======
##----------------------------------------------------------------------
## Service *MUST BE* enabled
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.cm.validators.clipsobject import CLIPSObjectValidator


class ServiceDisabledValidator(CLIPSObjectValidator):
    TITLE = "Service *MUST BE* enabled"
    DESCRIPTION = """
        Service must be enabled
    """
    TAGS = ["service"]
    RULES = """
    (defrule {{RULENAME}}
        ?s <- (service (name "{{service}}") (enabled 0))
        =>
        (assert
            (error (type "Service | Disabled")
                   (obj "{{service}}")))
    )
    """

    CONFIG_FORM = [
        {
            "name": "service",
            "xtype": "textfield",
            "fieldLabel": "Service",
            "allowBlank": False
        }
    ]
