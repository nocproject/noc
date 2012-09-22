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
from noc.lib.serialize import json_decode


class ExtApplication(Application):
    menu = None
    icon = "icon_application_form"
    ## HTTP Result Codes
    OK = 200
    CREATED = 201
    DELETED = 204
    BAD_REQUEST = 400
    FORBIDDEN = 401
    NOT_FOUND = 404
    CONFLICT = 409
    NOT_HERE = 410
    INTERNAL_ERROR = 500
    NOT_IMPLEMENTED = 501
    THROTTLED = 503
    ## Recognized GET parameters
    ignored_params = ["_dc"]
    page_param = "__page"
    start_param = "__start"
    limit_param = "__limit"
    sort_param = "__sort"
    format_param = "__format"  # List output format
    query_param = "__query"
    only_param = "__only"

    def __init__(self, *args, **kwargs):
        super(ExtApplication, self).__init__(*args, **kwargs)
        self.document_root = os.path.join(self.module, "apps", self.app)

    @property
    def js_app_class(self):
        m, a = self.get_app_id().split(".")
        return "NOC.%s.%s.Application" % (m, a)

    @property
    def launch_access(self):
        m, a = self.get_app_id().split(".")
        return HasPerm("%s:%s:launch" % (m, a))

    def deserialize(self, data):
        return json_decode(data)

    @view(url="^(?P<path>(?:js|css|img)/[0-9a-zA-Z_/]+\.(?:js|css|png))$",
          url_name="static", access=True)
    def view_static(self, request, path):
        """
        Static file server
        """
        return serve_static(request, path, document_root=self.document_root)
