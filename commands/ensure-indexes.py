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
        for model_id in iter_model_id():
            model = get_model(model_id)
            if not model:
                self.die("Invalid model: %s" % model_id)
            if not is_document(model):
                continue
            # Ensure only documents with auto_create_index == False
            if model._meta.get('auto_create_index', True):
                continue
            # Index model
            self.print("Checking indexes for %s" % model_id)
            model.ensure_indexes()
        # @todo: Detect changes
        self.print("OK")


if __name__ == "__main__":
    Command().run()
