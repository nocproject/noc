# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ./noc prefix-list
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from optparse import make_option
## Django modules
from django.core.management.base import BaseCommand, CommandError
# NOC modules
from noc.peer.models import WhoisCache
from noc.core.profile.loader import loader


class Command(BaseCommand):
    help = "CLI Prefix-list builder"
    option_list = BaseCommand.option_list + (
        make_option("--output", "-o", dest="output", action="store",
                    default="/dev/stdout",
                    help="Write output to file"),
        make_option("--profile", "-p", dest="profile",  action="store",
                    help="Device profile"),
        make_option("--name", "-n", dest="name", default="pl",  action="store",
                    help="prefix-list name")
    )

    def handle(self, *args, **options):
        # Check expression
        if len(args) != 1:
            raise CommandError("No expression given")
        expression = args[0]
        # Process profile
        if options["profile"] and loader.has_profile(options["profile"]):
            raise CommandError("Invalid profile: %s" % options["profile"])
        # Create output
        try:
            out = open(options["output"], "w")
        except IOError, why:
            raise CommandError(str(why))
        # Build
        self.build_prefix_list(out, expression, options["name"],
                               options["profile"])
        # Finalize
        out.close()

    def build_prefix_list(self, out, expression, name, profile):
        prefixes = WhoisCache.resolve_as_set_prefixes_maxlen(expression)
        if profile is None:
            l = "\n".join(p[0] for p in prefixes)
        else:
            l = loader.get_profile(profile)().generate_prefix_list(name, prefixes)
        if not l.endswith("\n"):
            l += "\n"
        out.write(l)
