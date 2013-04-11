# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Syncronize manifests
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.main.models.manifest import Manifest


class Command(BaseCommand):
    """
    ./noc sync-manifest
    """
    help = "Synchronize manifests"

    def handle(self, *args, **options):
        print "Synchronizing manifests"
        dmf = [
            m[:-9] for m in os.listdir("etc/manifests")
            if m.endswith(".defaults")
        ]
        mf = [
            m[:-5] for m in os.listdir("etc/manifests")
            if m.endswith(".conf")
        ]
        names = set(dmf) | set(mf)

        try:
            for name in names:
                print "   Manifest %s:" % name
                Manifest.update_manifest(name)
        except ValueError, why:
            raise CommandError(why)
