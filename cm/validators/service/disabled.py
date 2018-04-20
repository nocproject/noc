# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Service *MUST BE* disabled
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
=======
##----------------------------------------------------------------------
## Service *MUST BE* disabled
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.cm.validators.clipsobject import CLIPSObjectValidator


class ServiceDisabledValidator(CLIPSObjectValidator):
    TITLE = "Service *MUST BE* disabled"
    DESCRIPTION = """
        Service must be disabled
    """
    TAGS = ["service"]
    RULES = """
    (defrule {{RULENAME}}
        ?s <- (service (name "{{service}}") (enabled 1))
        =>
        (assert
            (error (type "Service | Enabled")
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
