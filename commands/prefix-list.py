# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ./noc prefix-list
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import print_function
# NOC modules
from noc.core.management.base import BaseCommand, CommandError
from noc.peer.models.whoiscache import WhoisCache
from noc.sa.models.profile import Profile


class Command(BaseCommand):
    help = "CLI Prefix-list builder"

    def add_arguments(self, parser):
        parser.add_argument("--output", "-o",
                            dest="output",
                            action="store",
                            default="/dev/stdout",
                            help="Write output to file"
                            ),
        parser.add_argument("--profile", "-p",
                            dest="profile",
                            action="store",
                            help="Device profile"
                            ),
        parser.add_argument("--name", "-n",
                            dest="output",
                            action="store",
                            default="pl",
                            help="prefix-list name"
                            ),

    def handle(self, *args, **options):
        # Check expression
        if len(args) != 1:
            raise CommandError("No expression given")
        expression = args[0]
        # Process profile
        profile = None
        if options["profile"]:
            profile = Profile.get_by_name(options["profile"])
            if not profile:
                raise CommandError("Invalid profile: %s" % options["profile"])
        # Create output
        try:
            out = open(options["output"], "w")
        except IOError as e:
            raise CommandError(str(e))
        # Build
        self.build_prefix_list(out, expression, options["name"],
                               profile)
        # Finalize
        out.close()

    def build_prefix_list(self, out, expression, name, profile):
        prefixes = WhoisCache.resolve_as_set_prefixes_maxlen(expression)
        if profile is None:
            ll = "\n".join(p[0] for p in prefixes)
        else:
            ll = profile.get_profile(profile)().generate_prefix_list(name, prefixes)
        if not ll.endswith("\n"):
            ll += "\n"
        out.write(ll)


if __name__ == "__main__":
    Command().run()
