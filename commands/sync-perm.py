# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Syncronize permissions
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.management.base import BaseCommand
from noc.main.models.permission import Permission
from noc.core.service.loader import get_service


class Command(BaseCommand):
    def handle(self, *args, **options):
        from noc.lib.app.site import site
        site.service = get_service()
        try:
            Permission.sync()
        except ValueError as e:
            self.die(str(e))


if __name__ == "__main__":
    Command().run()
