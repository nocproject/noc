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
            self.print("[%s] Checking indexes" % model_id)
            model.ensure_indexes()
        # @todo: Detect changes
        self.print("OK")


if __name__ == "__main__":
    Command().run()
