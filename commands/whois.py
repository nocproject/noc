# ---------------------------------------------------------------------
# ./noc whois
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import argparse

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect


class Command(BaseCommand):
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        subparsers.add_parser("update-cache")
        prefix_list_parser = subparsers.add_parser("prefix-list")
        prefix_list_parser.add_argument(
            "--profile", default="Cisco.IOS", help="Profile to generate"
        )
        prefix_list_parser.add_argument("--name", default="my-prefix-list", help="Prefix-list name")
        prefix_list_parser.add_argument("as_set", nargs=argparse.REMAINDER, help="AS-set")

    def handle(self, cmd, *args, **options):
        connect()
        return getattr(self, "handle_%s" % cmd.replace("-", "_"))(*args, **options)

    def handle_update_cache(self, *args, **options):
        from noc.core.whois import WhoisCacheLoader

        loader = WhoisCacheLoader()
        loader.update()

    def handle_prefix_list(self, as_set, name=None, profile=None, *args, **options):
        from noc.peer.models.whoiscache import WhoisCache
        from noc.sa.models.profile import Profile

        p = Profile.get_by_name(profile)
        if not p:
            self.die("Invalid profile %s" % profile)
        prefixes = WhoisCache.resolve_as_set_prefixes_maxlen(as_set[0])
        self.print(p.get_profile().generate_prefix_list(name, prefixes))


if __name__ == "__main__":
    Command().run()
