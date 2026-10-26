# ---------------------------------------------------------------------
# Synchronize permissions
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.aaa.models.permission import Permission
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.core.service.loader import get_service


class Command(BaseCommand):
    def handle(self, *args, **options):
        # NOC modules
        from noc.services.web.base.site import site

        connect()
        # Install service stub
        site.set_service(get_service())
        site.autodiscover()
        # Synchronize permissions
        try:
            Permission.sync()
        except ValueError as e:
            self.die(str(e))
