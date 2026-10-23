#!./bin/python
# ---------------------------------------------------------------------
# Web service
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from importlib.resources import files
import os
from typing import Any

# Third-party modules
from django.core.wsgi import get_wsgi_application
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

# NOC modules
from noc.config import config
from noc.core.service.base import BaseService
from noc.services.web.urls import set_url_patterns
from noc.main.models.customfield import CustomField
from noc.services.web.base.site import site


class WebService(BaseService):
    name = "web"
    api = []
    use_translation = True
    use_mongo = True
    use_router = True
    use_watchdog = config.watchdog.enable_watchdog

    def __init__(self) -> None:
        super().__init__()
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "noc.settings")
        self.wsgi_app = get_wsgi_application()
        self.extended_logging = True

    async def on_activate(self) -> None:
        # Initialize audit trail
        from noc.main.models.audittrail import AuditTrail

        AuditTrail.install()
        # Initialize site
        self.logger.info("Registering web applications")
        site.set_service(self)
        site.autodiscover()
        set_url_patterns(site.urls)
        # Install Custom fields
        CustomField.install_fields()

    def get_backend_weight(self):
        return config.web.max_threads

    def get_backend_limit(self):
        return config.web.max_threads

    def get_granian_options(self) -> dict[str, Any]:
        opts = super().get_granian_options().copy()
        ui_path = files("noc") / "ui"
        index_path = ui_path / f"index.{config.web.theme}.{config.web.language}.html"
        opts.update(
            {
                # Granian checks mounts in order, so the exact index route goes first.
                "static_path_route": ["/ui/index.html", "/index.html", "/ui"],
                "static_path_mount": [
                    index_path,
                    index_path,
                    ui_path,
                ],
                "static_path_expires": 604800,
            }
        )
        return opts

    def configure_api_routes(self, app: FastAPI) -> None:
        for path in ("/", "/main/desktop/"):
            app.add_api_route(
                path,
                self.redirect_to_index,
                methods=["GET", "HEAD"],
                include_in_schema=False,
            )

    async def redirect_to_index(self) -> RedirectResponse:
        return RedirectResponse("/index.html", status_code=301)
