# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Prefix.name
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
            "ip_prefix",
            "name",
            models.CharField(
                "Name",
                max_length=255,
                null=True, blank=True
            )
        )

    def backwards(self):
        pass
