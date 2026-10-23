# ----------------------------------------------------------------------
# Get sample devices for each platform
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.inv.models.platform import Platform
from noc.sa.models.profile import Profile
from noc.sa.models.managedobject import ManagedObject


class Command(BaseCommand):
    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "-s", "--sample", type=int, default=5, help="Amount of samples for each platform"
        )
        parser.add_argument("--platform", help="Fetch particular platform")
        parser.add_argument("--profile", help="Fetch particular profile")

        parser.add_argument(
            "--show",
            default="name",
            help="List of fields to show (name, platform, profile, address, version)",
        )

    def handle(self, sample=5, platform=None, profile=None, show=None, *args, **options):
        fields = show.split(",")
        connect()
        mqs = {"is_managed": True}
        pqs = {}
        if platform:
            p = Platform.objects.filter(name=platform).first()
            if not p:
                self.die(f"Invalid platform {platform}")
            pqs["name"] = platform
        if profile:
            p = Profile.objects.filter(name=profile).first()
            if not p:
                self.die(f"Invalid profile {profile}")
            mqs["profile"] = str(p.id)
        for platform in Platform.objects.filter(**pqs):
            qs = mqs.copy()
            qs["platform"] = platform.id
            x = 0
            for mo in ManagedObject.objects.filter(**qs).order_by("?"):
                r = []
                for f in fields:
                    if f == "name":
                        r.append(mo.name)
                    elif f == "address":
                        r.append(mo.address)
                    elif f == "platform":
                        r.append(mo.platform.full_name)
                    elif f == "profile":
                        r.append(mo.profile.name)
                    elif f == "version":
                        r.append(mo.version.version)
                self.print(",".join(r))
                x += 1
                if x >= sample:
                    break
