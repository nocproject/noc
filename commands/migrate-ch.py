# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# CH database schema migration tool
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
import os
# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.clickhouse.connect import connection
from noc.core.clickhouse.model import Model


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.connect()
        self.ensure_db()
        changed = self.ensure_bi_models()
        if changed:
            self.print("CHANGED")
        else:
            self.print("OK")

    def connect(self):
        """
        Connect to database
        :return: 
        """
        self.connect = connection()

    def ensure_db(self):
        """
        Ensure clickhouse database is exists
        :return: 
        """
        self.print("Ensuring database")
        self.connect.ensure_db()

    def ensure_bi_models(self):
        self.print("Ensuring BI models:")
        models = set()
        # Get models
        for f in os.listdir("bi/models"):
            if f.startswith("_") or not f.endswith(".py"):
                continue
            mn = f[:-3]
            model = Model.get_model_class(mn)
            if model:
                models.add(model)
        # Ensure fields
        changed = False
        for model in models:
            self.print("  * %s" % model._meta.db_table)
            changed |= model.ensure_table()
        return changed

if __name__ == "__main__":
    Command().run()
