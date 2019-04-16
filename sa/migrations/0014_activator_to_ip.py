# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# activator to ip
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from django.db import models
from south.db import db


class Migration(object):
    def forwards(self):
        db.add_column("sa_activator", "to_ip", models.IPAddressField("To IP", null=True, blank=True))
        db.execute("UPDATE sa_activator SET to_ip=ip")
        db.execute("ALTER TABLE sa_activator ALTER to_ip SET NOT NULL")

    def backwards(self):
        db.delete_column("sa_activator", "to_ip")
