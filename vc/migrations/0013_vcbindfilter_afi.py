# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# vcbindfilter afi
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
        db.add_column(
            "vc_vcbindfilter", "afi",
            models.CharField("Address Family", max_length=1, choices=[("4", "IPv4"), ("6", "IPv6")], default="4")
        )

    def backwards(self):
        db.delete_column("vc_vcbindfilter", "afi")
