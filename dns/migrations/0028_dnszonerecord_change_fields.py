# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# dnszonerecord change fields
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db
from django.db import models


class Migration(object):
    def forwards(self):
        db.rename_column("dns_dnszonerecord", "left", "name")
        db.rename_column("dns_dnszonerecord", "right", "content")
        db.execute(
            """
            ALTER TABLE dns_dnszonerecord
            ALTER COLUMN content TYPE VARCHAR(256)
            """
        )
        db.add_column("dns_dnszonerecord", "type", models.CharField("Type", max_length=16, default=""))

    def backwards(self):
        pass
