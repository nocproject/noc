# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# dnsserver generator_name
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
        db.add_column("dns_dnsserver", "generator_name", models.CharField("Generator", max_length=32, default="BINDv9"))
        db.execute("UPDATE dns_dnsserver SET generator_name=%s", ["BINDv9"])

    def backwards(self):
        raise NotImplementedError()
