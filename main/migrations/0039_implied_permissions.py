# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        db.add_column("main_permission", "implied",
                      models.CharField("Implied", max_length=256,
                                       null=True, blank=True))

    def backwards(self):
        db.delete_column("main_checkpoint", "implied")
