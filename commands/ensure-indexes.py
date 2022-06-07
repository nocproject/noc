# ----------------------------------------------------------------------
# Ensure MongoDB indexes
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.management.base import BaseCommand
from noc.models import get_model, iter_model_id, is_document
from noc.core.datastream.loader import loader as ds_loader
from noc.core.gridvcs.base import GridVCS
from noc.core.gridvcs.utils import REPOS
from noc.core.mongo.connection import connect, get_db
from noc.config import config


class Command(BaseCommand):
    def handle(self, host=None, port=None, *args, **options):
        connect()
        db = get_db()
        collections = set(db.list_collection_names())
        for model_id in iter_model_id():
            model = get_model(model_id)
            if not model:
                self.die("Invalid model: %s" % model_id)
            if not is_document(model):
                continue
            # Rename collections when necessary
            legacy_collections = model._meta.get("legacy_collections", [])
            for old_name in legacy_collections:
                if old_name in collections:
                    new_name = model._meta["collection"]
                    self.print("[%s] Renaming %s to %s" % (model_id, old_name, new_name))
                    db[old_name].rename(new_name)
                    break
            # Ensure only documents with auto_create_index == False
            if model._meta.get("auto_create_index", True):
                continue
            # Index model
            self.index_model(model_id, model)
        # Index datastreams
        self.index_datastreams()
        # Index GridVCS
        self.index_gridvcs()
        # Index mongo cache
        self.index_cache()
        # Index RCA lock
        self.index_rca_lock()
        # @todo: Detect changes
        self.print("OK")

    def index_model(self, model_id, model):
        """
        Create necessary indexes for model
        :param model_id: model id
        :param model: model class
        :return:
        """
        self.print("[%s] Checking indexes" % model_id)
        coll = model._get_collection()
        # Get existing unique indexes
        idx_info = coll.index_information()
        x_name = {}  # fields -> name
        x_unique = {}  # fields -> bool(is_unique)
        left_unique = set()
        for xn in idx_info:
            fields = ",".join(str(k[0]) for k in idx_info[xn]["key"])
            x_name[fields] = xn
            is_unique = idx_info[xn].get("unique", False)
            x_unique[fields] = is_unique
            if is_unique:
                left_unique.add(fields)
        if x_name:
            # Get declared indexes
            xspecs = model._meta["index_specs"]
            for xi in xspecs:
                fields = ",".join(str(k[0]) for k in xi["fields"])
                if fields in x_name:
                    # Check for uniqueness match
                    du = xi.get("unique", False)
                    if du != x_unique[fields]:
                        # Uniqueness mismatch
                        self.print("[%s] Dropping mismatched index %s" % (model_id, x_name[fields]))
                        coll.drop_index(x_name[fields])
                    elif du and x_unique[fields]:
                        # Remove unique index from left
                        left_unique.remove(fields)
            # Delete state unique indexes
            for fields in left_unique:
                self.print("[%s] Dropping stale unique index %s" % (model_id, x_name[fields]))
                coll.drop_index(x_name[fields])
        # Apply indexes
        model.ensure_indexes()

    def index_datastreams(self):
        for name in ds_loader:
            if not getattr(config.datastream, "enable_%s" % name, False):
                continue
            ds = ds_loader[name]
            self.print("[%s] Indexing datastream" % ds.name)
            ds.ensure_collection()

    def index_gridvcs(self):
        for repo in REPOS:
            GridVCS(repo).ensure_collection()

    def index_cache(self):
        from noc.core.cache.base import cache

        if not hasattr(cache, "ensure_indexes"):
            return
        self.print("[%s] Indexing cache" % cache.__class__.__name__)
        cache.ensure_indexes()

    def index_rca_lock(self):
        from noc.services.correlator.rcalock import RCALock

        self.print("[RCA Lock] Indexing")
        RCALock.create_indexes()


if __name__ == "__main__":
    Command().run()
