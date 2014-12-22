# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## Third-party modules
from south.db import db


class Migration:

    def forwards(self):
        db.add_column(
            "sa_maptask", "script_timeout",
            models.IntegerField(_("Script timeout"), null=True, blank=True)
        )

    def backwards(self):
        db.delete_column("sa_maptask", "script_timeout")
