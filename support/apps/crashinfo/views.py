# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## support.crashinfo application
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import uuid
## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.support.models.crashinfo import Crashinfo


class CrashinfoApplication(ExtDocApplication):
    """
    Crashinfo application
    """
    title = "Crashinfo"
    menu = "Crashinfo"
    model = Crashinfo

    @view(url="^(?P<id>\S+)/traceback/", method=["GET"],
          access="read", api=True)
    def api_traceback(self, request, id):
        ci = self.get_object_or_404(Crashinfo, uuid=uuid.UUID(id))
        return ci.traceback
