# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Syncronize permissions
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Django modules
from django.core.management.base import BaseCommand, CommandError
# NOC modules
from noc.lib.app.site import site
from noc.main.models.permission import Permission


class Command(BaseCommand):
    """
    ./noc sync-perm
    """
    help = "Synchronize permissions"

    def handle(self, *args, **options):
        try:
            Permission.sync()
        except ValueError, why:
            raise CommandError(why)
