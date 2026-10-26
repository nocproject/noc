# ---------------------------------------------------------------------
# inv.inv plugins
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging

# Third-party modules
from django.http import HttpRequest
from gufo.loader import Loader

# NOC modules
from noc.config import config
from noc.core.feature import Feature
from noc.inv.models.object import Object

from ..views import InvApplication


class InvPlugin:
    name = None
    js = None
    required_feature: Feature | None = None

    def __init__(self, app: InvApplication) -> None:
        self.app = app
        self.logger = logging.getLogger(f"{__name__.rsplit('.', 1)[0]}.{self.name}")
        self.init_plugin()

    def set_app(self, app: InvApplication):
        pass

    def add_view(self, name, func, url, method=["GET"], access="read", validate=None):
        self.app.add_view(name, func, url=url, method=method, access=access, validate=validate)

    def init_plugin(self):
        self.add_view(
            f"api_plugin_{self.name}_data",
            self.api_get_data,
            url=f"^(?P<id>[0-9a-f]{{24}})/plugin/{self.name}/$",
        )

    def api_get_data(self, request: HttpRequest, id):
        o = self.app.get_object_or_404(Object, id=id)
        return self.get_data(request, o)

    def get_data(self, request: HttpRequest, object):
        return None


inv_plugin_loader = Loader[type[InvPlugin]](
    bases=config.iter_customized_bases("noc.services.web.apps.inv.inv.plugins"),
    exclude=("base",),
)
