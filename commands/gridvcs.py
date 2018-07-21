# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Full-text search index management
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import print_function
import argparse
import os
# NOC modules
from noc.core.management.base import BaseCommand, CommandError
from noc.sa.models.managedobject import ManagedObject
from noc.lib.validators import is_int
from noc.config import config
from noc.core.fileutils import safe_rewrite


class Command(BaseCommand):
    """
    Manage Jobs
    """
    help = "Manage GridVCS config repo"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        parser.add_argument("--repo", "-r",
                            dest="repo",
                            action="store",
                            default="sa.managedobject.config",
                            help="Apply to repo"
                            ),
        # mirror command
        sp_mirr = subparsers.add_parser("mirror", help="Mirror repo")
        sp_mirr.add_argument("-split", help="Split config by Pool/Adm. Domain", default="")
        # get command
        sp_get = subparsers.add_parser("get", help="Get current value")
        sp_get.add_argument(
            "args",
            nargs=argparse.REMAINDER,
            help="List of extractor names"
        )

    def out(self, msg):
        if not self.verbose_level:
            return
        print(msg)

    def handle(self, *args, **options):
        self.repo = options.get("repo")
        self.split = options.get("split")
        if not self.repo or self.repo not in ["sa.managedobject.config"]:
            raise CommandError("Invalid repo")
        return getattr(self, "handle_%s" % options["cmd"])(args)

    def get_object(self, id):
        def _get(model, fields, o_id):
            for f in fields:
                try:
                    return model.objects.get(**{f: o_id})
                except model.DoesNotExist:
                    pass
            if is_int(id):
                try:
                    return model.objects.get(id=id)
                except model.DoesNotExist:
                    pass
            return None

        if self.repo == "sa.managedobject.config":
            return _get(ManagedObject, ["name"], id)

    def get_value(self, object):
        if self.repo == "sa.managedobject.config":
            return object.config.read()

    def handle_mirror(self, *args):
        mirror = config.path.config_mirror_path
        if not mirror:
            raise CommandError("No mirror path set")
        mirror = os.path.realpath(mirror)
        self.out("Mirroring")
        if self.repo == "sa.managedobject.config":
            for o in ManagedObject.objects.filter(is_managed=True):
                v = self.get_value(o)
                if v:
                    if self.split == 'pool':
                        mpath = os.path.realpath(
                            os.path.join(mirror, unicode(o.pool.name), unicode(o)))
                    else:
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
            print(self.get_value(o))


if __name__ == "__main__":
    Command().run()
