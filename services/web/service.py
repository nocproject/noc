#!./bin/python
# ---------------------------------------------------------------------
# Web service
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os

# Third-party modules
from django.core.wsgi import get_wsgi_application

# NOC modules
from noc.config import config
from noc.core.service.fastapi import FastAPIService
from noc.main.models.customfield import CustomField


class WebService(FastAPIService):
    name = "web"
    api = []
    use_translation = True
    use_mongo = True
    use_router = True
    use_watchdog = config.watchdog.enable_watchdog
    traefik_routes_rule = "!PathPrefix(`/api/`) && !PathPrefix(`/ui/`) && PathPrefix(`/`)"

    def __init__(self):
        super().__init__()
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "noc.settings")
        self.wsgi_app = get_wsgi_application()
        self.extended_logging = True

    async def on_activate(self):
        # Initialize audit trail
        from noc.main.models.audittrail import AuditTrail

        AuditTrail.install()
        # Initialize site
        self.logger.info("Registering web applications")
        from noc.services.web.base.site import site

        site.service = self
        site.autodiscover()
        # Install Custom fields
        CustomField.install_fields()

    def get_backend_weight(self):
        return config.web.max_threads

    def get_backend_limit(self):
        return config.web.max_threads


if __name__ == "__main__":
    WebService().start()
