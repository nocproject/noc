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

    @view(url="^(?P<id>[0-9a-f]{24})/json/$", method=["GET"],
          access="read", api=True)
    def api_json(self, request, id):
        et = self.get_object_or_404(ErrorType, id=id)
        return et.to_json()
