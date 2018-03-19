# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Address.name field
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from south.db import db
from django.db import models


class Migration(object):
    def forwards(self):
        db.add_column(
            "ip_address",
            "name",
            models.CharField(
                "Name",
                max_length=255,
                null=True, blank=True
            )
        )
        db.execute("UPDATE ip_address SET name = fqdn")
        db.execute("ALTER TABLE ip_address ALTER name SET NOT NULL")
        db.execute("ALTER TABLE ip_address ALTER fqdn DROP NOT NULL")

    def backwards(self):
        pass
