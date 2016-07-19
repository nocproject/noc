# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Collections manipulation
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
from collections import namedtuple
import argparse
## Third-party modules
import ujson
from mongoengine.fields import ListField, EmbeddedDocumentField
## NOC modules
from noc.core.management.base import BaseCommand
from noc.core.collection.base import Collection


class Command(BaseCommand):
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            dest="cmd",
            help="sub-commands help"
        )
        # sync
        sync_parser = subparsers.add_parser(
            "sync",
            help="Synchronize collections"
        )
        # install
        install_parser = subparsers.add_parser(
            "install",
            help="Add collections to repository"
        )
        install_parser.add_argument(
            "-r", "--remove",
            dest="remove",
            action="store_true",
            help="Remove installed files"
        )
        install_parser.add_argument(
            "-l", "--load",
            dest="load",
            action="store_true",
            help="Load to database"
        )
        install_parser.add_argument(
            "install_files",
            nargs=argparse.REMAINDER,
            help="List of files"
        )

    def handle(self, cmd, *args, **options):
        getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_sync(self):
        for c in Collection.iter_collections():
            try:
                c.sync()
            except ValueError as e:
                self.die(str(e))

    def handle_install(self, install_files=None, remove=False, load=False):
        install_files = install_files or []
        for fp in install_files:
            if not os.path.isfile(fp):
                self.die("File not found: %s" % fp)
            with open(fp) as f:
                data = ujson.load(f)
            Collection.install(data)
            if load:
                c = Collection(data["$collection"])
                c.update_item(data)
            if remove:
                os.unlink(fp)

if __name__ == "__main__":
    Command().run()
