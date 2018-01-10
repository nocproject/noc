# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Ensure MongoDB indexes
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
# NOC modules
from noc.core.management.base import BaseCommand
from noc.models import get_model, iter_model_id, is_document


class Command(BaseCommand):
    def handle(self, host=None, port=None, *args, **options):
        from noc.lib.nosql import get_db

        db = get_db()
        collections = set(db.collection_names())
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
            if model._meta.get('auto_create_index', True):
                continue
            # Index model
            self.index_model(model_id, model)
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
        x_indexes = {}  # fields -> name
        for xn in idx_info:
            if idx_info[xn].get("unique", False):
                fields = ",".join(str(k[0]) for k in idx_info[xn]["key"])
                x_indexes[fields] = xn
        # Get declared unique indexes
        if x_indexes:
            xspecs = model._meta["index_specs"]
            for xi in xspecs:
                if not xi.get("unique", False):
                    continue
                fields = ",".join(str(k[0]) for k in xi["fields"])
                if fields in x_indexes:
                    del x_indexes[fields]
            # Delete state unique indexes
            for fn in x_indexes:
                self.print("[%s] Drop stale unique index %s" % (model_id, x_indexes[fn]))
                coll.drop_index(x_indexes[fn])
        # Apply indexes
        model.ensure_indexes()
        #self.print("[%s] Indexes: %s || %s" % (model_id, model.list_indexes(), model._get_collection().index_information()))

if __name__ == "__main__":
    Command().run()
