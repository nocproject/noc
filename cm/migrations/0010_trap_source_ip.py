# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        db.add_column("cm_config", "trap_source_ip", models.IPAddressField("Trap Source IP", blank=True, null=True))
        db.add_column("cm_config", "trap_community",
                      models.CharField("Trap Community", blank=True, null=True, max_length=64))

    def backwards(self):
        db.delete_column("cm_config", "trap_source_ip")
        db.delete_column("cm_config", "trap_community")
