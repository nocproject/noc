# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Full-text search index management
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from optparse import make_option
import os
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.sa.models import ManagedObject
from noc.lib.validators import is_int
from noc.settings import config
from noc.lib.fileutils import safe_rewrite


class Command(BaseCommand):
    """
    Manage Jobs
    """
    help = "Manage Full-Text Search index"
    option_list=BaseCommand.option_list+(
        make_option(
            "--repo", "-r",
            action="store",
            dest="repo",
            default="sa.managedobject.config",
            help="Apply to repo"
        ),
        make_option(
            "--mirror", "-M",
            action="store_const",
            dest="action",
            const="mirror",
            help="Mirror repo"
        ),
        make_option(
            "--get", "-g",
            action="store_const",
            dest="action",
            const="get",
            help="Get current value"
        )
    )

    def out(self, msg):
        if not self.verbose:
            return
        print msg

    def handle(self, *args, **options):
        self.verbose = bool(options.get("verbosity"))
        self.repo = options.get("repo")
        if not self.repo or self.repo not in ["sa.managedobject.config"]:
            raise CommandError("Invalid repo")
        if "action" in options:
            if options["action"] == "mirror":
                self.handle_mirror()
            elif options["action"] == "get":
                self.handle_get(args)

    def get_object(self, id):
        def _get(model, fields, o_id):
            for f in fields:
                try:
                    return model.objects.get(**{f: o_id})
                except model.DoesNotExist:
                    pass
            if is_int(id):
                try:
                    return model.objects.get(id=o.id)
                except model.DoesNotExist:
                    pass
            return None

        if self.repo == "sa.managedobject.config":
            return _get(ManagedObject, ["name"], id)

    def get_value(self, object):
        if self.repo == "sa.managedobject.config":
            return object.config.read()

    def handle_mirror(self):
        mirror = config.get("gridvcs", "mirror.%s" % self.repo) or None
        if not mirror:
            raise CommandError("No mirror path set")
        mirror = os.path.realpath(mirror)
        self.out("Mirroring")
        if self.repo == "sa.managedobject.config":
            for o in ManagedObject.objects.filter(is_managed=True):
                v = self.get_value(o)
                if v:
                    mpath = os.path.realpath(
                        os.path.join(mirror, unicode(o)))
                    if mpath.startswith(mirror):
                        self.out("   mirroring %s" % o)
                        safe_rewrite(mpath, v)
                    else:
                        self.out("    !!! mirror path violation for" % o)
        self.out("Done")

    def handle_get(self, objects):
        ol = []
        for o_id in objects:
            o = self.get_object(o_id)
            if not o:
                raise CommandError("Object not found: %s" % o_id)
            ol += [o]
        for o in ol:
            print self.get_value(o)
