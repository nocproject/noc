# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Upload bundled MIBs
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.fm.models import MIB, MIBRequiredException


class Command(BaseCommand):
    help = "Upload bundled MIBs"

    def handle(self, *args, **options):
        self.sync_mibs()

    def sync_mibs(self):
        """
        Upload bundled MIBs
        """
        # Loaded MIBs cache
        loaded_mibs = set([m.name for m in MIB.objects.all()])
        # Enumerate local stored MIBs
        prefix = os.path.join("share", "mibs")
        new_mibs = {}
        for m in os.listdir(prefix):
            mib_name, ext = os.path.splitext(m)
            if mib_name not in loaded_mibs:
                # Try to upload new MIB
                try:
                    MIB.load(os.path.join(prefix, m))
                    loaded_mibs.add(mib_name)
                    print "UPLOAD MIB %s" % mib_name
                except MIBRequiredException, x:
                    new_mibs[mib_name] = x.requires_mib
        # Try to load new MIBs
        while new_mibs:
            l_new_mibs = len(new_mibs)
            for mib_name, requires_mib in new_mibs.items():
                if requires_mib in loaded_mibs:
                    try:
                        MIB.load(os.path.join(prefix, mib_name + ".mib"))
                        loaded_mibs.add(mib_name)
                        print "UPLOAD MIB %s" % mib_name
                        del new_mibs[mib_name]
                    except MIBRequiredException, x:
                        new_mibs[mib_name] = x.requires_mib
            if len(new_mibs) == l_new_mibs:  # No new MIBs loaded
                raise CommandError("Following builtin MIBs cannot be loaded: %s" % " ".join(new_mibs))
