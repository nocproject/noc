# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Add CommandSnippet.ignore_cli_errors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from django.db import models
# Third-party modules
from south.db import db


class Migration:
    def forwards(self):
        db.add_column("sa_commandsnippet", "ignore_cli_errors",
                      models.BooleanField("Ignore CLI errors", default=False))

    def backwards(self):
        db.delete_column("sa_commandsnippet", "ignore_cli_errors")
