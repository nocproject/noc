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
from access import PermitLogged


class ExtApplication(Application):
    menu = None
    icon = "icon_application_form"

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

    @view(url="^permissions/$", method=["GET"], access=PermitLogged(),
          api=True)
    def api_permissions(self, request):
        """
        Get user permissions to given application
        
        :returns: List of strings with permissions names
        """
        from noc.main.models import Permission

        ps = self.get_app_id().replace(".", ":") + ":"
        if request.user.is_superuser:
            qs = Permission.objects
        else:
            qs = request.user.noc_user_permissions
        return [p.split(":")[2] for p in
                qs.filter(name__startswith = ps).values_list("name", flat=True)]

    @view(url="^(?P<path>(?:js|css|img)/[0-9a-zA-Z_/]+\.(?:js|css|png))$",
          url_name="static", access=True)
    def view_static(self, request, path):
        """
        Static file server
        """
        return serve_static(request, path, document_root=self.document_root)
