# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Get sample devices for each platform
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
# NOC modules
from noc.core.management.base import BaseCommand
from noc.inv.models.platform import Platform
from noc.sa.models.profile import Profile
from noc.sa.models.managedobject import ManagedObject


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "-s",
            "--sample",
            type=int,
            default=5,
            help="Amount of samples for each platform"
        )
        parser.add_argument(
            "--platform",
            help="Fetch particular platform"
        )
        parser.add_argument(
            "--profile",
            help="Fetch particular profile"
        )

        parser.add_argument(
            "--show",
            default="name",
            help="List of fields to show (name, platform, profile, address, version)"
        )

    def handle(self, sample=5, platform=None, profile=None, show=None,
               *args, **options):
        fields = show.split(",")
        mqs = {
            "is_managed": True
        }
        pqs = {}
        if platform:
            p = Platform.objects.filter(name=platform).first()
            if not p:
                self.die("Invalid platform %s" % platform)
            pqs["name"] = platform
        if profile:
            p = Profile.objects.filter(name=profile).first()
            if not p:
                self.die("Invalid profile %s" % profile)
            mqs["profile"] = str(p.id)
        for platform in Platform.objects.filter(**pqs):
            qs = mqs.copy()
            qs["platform"] = platform.id
            x = 0
            for mo in ManagedObject.objects.filter(**qs).order_by("?"):
                r = []
                for f in fields:
                    if f == "name":
                        r += [mo.name]
                    elif f == "address":
                        r += [mo.address]
                    elif f == "platform":
                        r += [mo.platform.full_name]
                    elif f == "profile":
                        r += [mo.profile.name]
                    elif f == "version":
                        r += [mo.version.version]
                self.print(",".join(r))
                x += 1
                if x >= sample:
                    break


if __name__ == "__main__":
    Command().run()
