# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## cm.errortype application
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.cm.models.errortype import ErrorType


class ErrorTypeApplication(ExtDocApplication):
    """
    ErrorType application
    """
    title = "Error Type"
    menu = "Setup | Error Types"
    model = ErrorType
