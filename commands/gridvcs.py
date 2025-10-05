# ---------------------------------------------------------------------
# Full-text search index management
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import argparse
import datetime
import os
from typing import List

# Third-party modules
import bson
from pymongo import DESCENDING

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.core.gridvcs.base import GridVCS
from noc.core.gridvcs.utils import REPOS
from noc.core.fileutils import safe_rewrite
from noc.core.validators import is_objectid

MBYTE_MULTIPLIER = 1024 * 1024


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
        subparsers = parser.add_subparsers(dest="cmd", required=True)
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
        stat_parser = subparsers.add_parser("stats", help="Show stats")
        stat_parser.add_argument("--top", default=0, type=int, help="Top device by size")
        bucket_parser = subparsers.add_parser("bucket", help="Show stats by buckets")
        bucket_parser.add_argument("--backets", default=5, help="Bucket count")
        bucket_parser.add_argument(
            "--min-size", default=128000, type=int, help="Top device by size"
        )
        bucket_parser.add_argument(
            "--detail", default=False, action="store_true", help="Show bucket elements"
        )
        # mirror command
        sp_mirr = subparsers.add_parser("mirror", help="Mirror repo")
        sp_mirr.add_argument(
            "--split", action="store_true", default=False, help="Add pool name to path"
        )
        sp_mirr.add_argument("--path", help="Path to folder", default="/tmp/cfg_mirror")
        # Forget History command
        forget_parser = subparsers.add_parser(
            "forget-history", help="Forget revisions after revision"
        )
        forget_parser.add_argument(
            "--before-days", type=int, help="Revision or Date", required=True
        )
        forget_parser.add_argument(
            "--approve", action="store_true", default=False, help="Do not modify data"
        )
        forget_parser.add_argument("--include-labels", help="Labels for additional filter")
        forget_parser.add_argument("--exclude-labels", help="Labels for exclude additional filter")
        forget_parser.add_argument("objects", nargs=argparse.REMAINDER, help="ManagedObject ids")

    def out(self, msg):
        if not self.verbose_level:
            return
        print(msg)

    def handle(self, *args, **options):
        self.repo = options["repo"]
        connect()
        self.vcs = GridVCS(self.repo)
        if self.repo in self.clean_int:
            self.clean_id = lambda y: int(y)
        else:
            self.clean_id = lambda y: y
        return getattr(self, f"handle_{options['cmd'].replace('-', '_')}")(*args, **options)

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

    def handle_stats(self, *args, top=25, **options):
        files = self.vcs.fs._GridFS__files
        chunks = self.vcs.fs._GridFS__chunks
        db = files.database
        obj_count = len(files.distinct("object"))
        rev_count = files.estimated_document_count()
        chunks_count = chunks.estimated_document_count()
        fstats = db.command("collstats", files.name)
        cstats = db.command("collstats", chunks.name)
        ssize = fstats["storageSize"] + cstats["storageSize"]
        self.print(f"%s repo summary: {self.repo}")
        self.print(f"Objects  : {obj_count}")
        self.print(f"Revisions: {rev_count} (%.2f rev/object)" % (float(rev_count) / obj_count))
        self.print(f"Chunks   : {chunks_count}")
        self.print(
            f"Size     : {round(ssize / MBYTE_MULTIPLIER, 3)} Mb (%d bytes/object)"
            % int(ssize / obj_count)
        )
        if top:
            self.print(f"Top {top}")
            for t in files.aggregate(
                [
                    {"$group": {"_id": "$object", "size": {"$sum": "$length"}}},
                    {"$sort": {"size": -1}},
                    {"$limit": top},
                ]
            ):
                o = self.clean_id(t["_id"])
                if self.repo == "config":
                    from noc.sa.models.managedobject import ManagedObject

                    o = ManagedObject.objects.get(id=o)
                self.print("Object '%s' : %d kbytes)" % (o, int(t["size"] / 1024)))

    def handle_bucket(self, min_size=128000, buckets=5, detail=False, *args, **options):
        r = self.get_bucket(buckets=buckets, min_size=min_size)
        for num, bucket in enumerate(r):
            self.print("\n", "=" * 80)
            self.print(
                f"Bucket {num}:    Count: %d; Size %d kb - %d kb"
                % (bucket["count"], bucket["_id"]["min"] / 1024, bucket["_id"]["max"] / 1024)
            )
            if detail:
                for o in bucket["objects"]:
                    if self.repo == "config":
                        from noc.sa.models.managedobject import ManagedObject

                        o = ManagedObject.objects.get(id=o)
                    self.print(f"Object:  {o}")
            else:
                self.print("Ids: ", ",".join(str(x) for x in bucket["objects"]))

    def get_bucket(self, min_size=None, buckets=5):
        return self.vcs.fs._GridFS__files.aggregate(
            [
                {"$group": {"_id": "$object", "size": {"$sum": "$length"}}},
                {"$match": {"size": {"$gte": min_size}}},
                {
                    "$bucketAuto": {
                        "groupBy": "$size",
                        "buckets": buckets,
                        "output": {"count": {"$sum": 1}, "objects": {"$push": "$_id"}},
                    }
                },
            ]
        )

    def handle_mirror(self, split=False, path=None, *args, **options):
        from noc.sa.models.managedobject import ManagedObject
        from noc.main.models.pool import Pool

        mirror = os.path.realpath(path)
        self.print("Mirroring to %s" % path)
        if self.repo == "config":
            for o_id, address, pool in self.progress(
                ManagedObject.objects.filter().values_list("id", "address", "pool")
            ):
                pool = Pool.get_by_id(pool)
                data = self.vcs.get(self.clean_id(o_id))
                if data:
                    if split:
                        mpath = os.path.realpath(os.path.join(mirror, str(pool), str(address)))
                    else:
                        mpath = os.path.realpath(os.path.join(mirror, str(address)))
                    if mpath.startswith(mirror):
                        safe_rewrite(mpath, data)
                    else:
                        self.print("    !!! mirror path violation for" % address)
        self.print("Done")

    def _forget(self, mo, revision: str, dry_run=False):
        def forget(f_rev):
            if dry_run:
                # self.print(f"[{mo.name}] Forgetting revision {f_rev.id} ({f_rev.ts.isoformat()})")
                return
            self.vcs.fs.delete(f_rev.id)

        rev = self.vcs.find_revision(mo.id, str(revision))
        if not rev:
            self.die(f"[{mo.name}] Revision {revision!s} is not found")
        if rev.ft != GridVCS.T_FILE:
            # End revision is delta
            data = self.vcs.get(mo.id, rev)
            # Drop from revision
            num = 0
            for num, r in enumerate(self.vcs.iter_revisions(mo.id, reverse=True)):
                if r.ts <= rev.ts:
                    forget(r)
            self.print(f"[{mo.name}] Forgetting {num} revisions")
            if not dry_run:
                self.vcs.fs.put(
                    self.vcs.compress(data.encode("utf-8"), self.vcs.DEFAULT_COMPRESS),
                    object=mo.id,
                    ts=rev.ts,
                    ft=self.vcs.T_FILE,
                    encoding=self.vcs.ENCODING,
                    c=self.vcs.DEFAULT_COMPRESS,
                )
        else:
            # Full snapshot, drop tail
            for r in self.vcs.iter_revisions(mo.id, reverse=True):
                if r.ts < rev.ts:
                    forget(r)

    def handle_forget_history(
        self,
        objects: List[str],
        before_days: int = None,
        before_revision: str = None,
        approve=False,
        include_labels=None,
        exclude_labels=None,
        *args,
        **options,
    ):
        from noc.inv.models.resourcegroup import ResourceGroup

        if not before_days and not before_revision:
            self.die("Revision or before days is not set")
        if before_days:
            # Timestamp
            # before = parse(before)
            before = datetime.datetime.now() - datetime.timedelta(days=before_days)
            before = bson.ObjectId.from_datetime(before)
        elif before_revision and is_objectid(before_revision):
            # Timestamp
            # before = parse(before)
            before = bson.ObjectId(before_revision)
        if include_labels:
            include_labels = include_labels.split(",")
        if exclude_labels:
            exclude_labels = exclude_labels.split(",")
        for oo in objects:
            oos = ResourceGroup.get_objects_from_expression(
                oo, "sa.ManagedObject", include_labels=include_labels, exclude_labels=exclude_labels
            )
            if not oos:
                self.print(f"Object with id {objects} not found. Next...")
                continue
            for mo in oos:
                self.print(f"[{mo.name}] Processed")
                r = self.vcs.files.find_one(
                    {"object": mo.id, "_id": {"$lte": before}},
                    {"_id": 1},
                    sort=[("ts", DESCENDING)],
                )
                # self.print("Revision", r)
                if not r:
                    self.print(f"[{mo.name}] Not found revision. Continue")
                    continue
                self._forget(mo, r["_id"], dry_run=not approve)


if __name__ == "__main__":
    Command().run()
