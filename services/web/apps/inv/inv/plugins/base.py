# ---------------------------------------------------------------------
# inv.inv plugins
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging

# NOC modules
from noc.inv.models.object import Object


class InvPlugin(object):
    name = None
    js = None

    def __init__(self, app):
        self.app = app
        self.logger = logging.getLogger("%s.%s" % (__name__.rsplit(".", 1)[0], self.name))
        self.init_plugin()

    def set_app(self, app):
        pass

    def add_view(self, name, func, url, method=["GET"], access="read", validate=None):
        self.app.add_view(name, func, url=url, method=method, access=access, validate=validate)

    def init_plugin(self):
        self.add_view(
            f"api_plugin_{self.name}_data",
            self.api_get_data,
            url=f"^(?P<id>[0-9a-f]{{24}})/plugin/{self.name}/$",
        )

    def api_get_data(self, request, id):
        o = self.app.get_object_or_404(Object, id=id)
        return self.get_data(request, o)

    def get_data(self, request, object):
        return None
