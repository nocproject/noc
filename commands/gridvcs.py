# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Full-text search index management
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import print_function
import argparse

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.gridvcs.base import GridVCS
from noc.core.gridvcs.utils import REPOS


class Command(BaseCommand):
    """
    Manage Jobs
    """

    help = "Manage GridVCS config repo"

    clean_int = {
        "rpsl_as",
        "rpsl_asset",
        "rpsl_peer",
        "rpsl_person",
        "rpsl_maintainer",
        "dnszone",
        "config",
        "object_comment",
    }

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        parser.add_argument(
            "--repo",
            "-r",
            dest="repo",
            action="store",
            choices=REPOS,
            default="config",
            help="Apply to repo",
        )
        # get command
        show_parser = subparsers.add_parser("show", help="Show current value")
        show_parser.add_argument("args", nargs=argparse.REMAINDER, help="List of extractor names")
        # compress command
        subparsers.add_parser("compress", help="Apply compression")
        # stats command
        subparsers.add_parser("stats", help="Show stats")

    def out(self, msg):
        if not self.verbose_level:
            return
        print(msg)

    def handle(self, *args, **options):
        self.repo = options["repo"]
        self.vcs = GridVCS(self.repo)
        if self.repo in self.clean_int:
            self.clean_id = lambda y: int(y)
        else:
            self.clean_id = lambda y: y
        return getattr(self, "handle_%s" % options["cmd"])(*args, **options)

    def handle_show(self, *args, **options):
        for o_id in args:
            data = self.vcs.get(self.clean_id(o_id))
            if data:
                self.print("@@@ %s" % o_id)
                self.print(data)

    def handle_compress(self, *args, **options):
        to_compress = [
            d["_id"]
            for d in self.vcs.fs._GridFS__files.aggregate(
                [{"$match": {"c": {"$exists": False}}}, {"$group": {"_id": "$object"}}]
            )
        ]
        if not to_compress:
            self.print("Nothing to compress")
            return
        for obj in self.progress(to_compress):
            self.compress_obj(obj)

    def compress_obj(self, obj):
        revs = list(self.vcs.iter_revisions(obj))
        data = [(self.vcs.get(obj, r), r) for r in revs]
        self.vcs.delete(obj)
        for cfg, rev in data:
            if cfg:
                self.vcs.put(obj, cfg, rev.ts)

    def handle_stats(self, *args, **options):
        files = self.vcs.fs._GridFS__files
        chunks = self.vcs.fs._GridFS__chunks
        db = files.database
        obj_count = len(files.distinct("object"))
        rev_count = files.estimated_document_count()
        chunks_count = chunks.estimated_document_count()
        fstats = db.command("collstats", files.name)
        cstats = db.command("collstats", chunks.name)
        ssize = fstats["storageSize"] + cstats["storageSize"]
        self.print("%s repo summary:" % self.repo)
        self.print("Objects  : %d" % obj_count)
        self.print("Revisions: %d (%.2f rev/object)" % (rev_count, float(rev_count) / obj_count))
        self.print("Chunks   : %d" % chunks_count)
        self.print("Size     : %d (%d bytes/object)" % (ssize, int(ssize / obj_count)))


if __name__ == "__main__":
    Command().run()
