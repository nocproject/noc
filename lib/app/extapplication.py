# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ExtApplication implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## Django modules
from django.views.static import serve as serve_static
## NOC modules
from application import Application, view, HasPerm
from access import Permit


class ExtApplication(Application):
    menu = None

    def __init__(self, *args, **kwargs):
        super(ExtApplication, self).__init__(*args, **kwargs)
        self.document_root = os.path.join(self.module, "apps", self.app)

    @property
    def launch_info(self):
        m, a = self.get_app_id().split(".")
        return {
            "class": "NOC.%s.%s.Application" % (m, a),
            "title": unicode(self.title),
            "params": {}
        }

    @property
    def launch_access(self):
        m, a = self.get_app_id().split(".")
        return HasPerm("%s:%s:launch" % (m, a))

    @view(url="^(?P<path>(?:js|css|img)/[0-9a-zA-Z/]+.js)", url_name="static",
          access=Permit())
    def view_static(self, request, path):
        """
        Static file server
        """
        return serve_static(request, path, document_root=self.document_root)
