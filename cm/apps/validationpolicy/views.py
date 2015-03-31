# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## cm.validationpolicy application
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.cm.models.validationpolicy import ValidationPolicy


class ValidationPolicyApplication(ExtDocApplication):
    """
    ValidationPolicy application
    """
    title = "Validation Policy"
    menu = "Setup | Validation Policy"
    model = ValidationPolicy
