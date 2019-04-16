# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# dnszoneprofile description
# ----------------------------------------------------------------------
# Copyright (C) 2009-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db
from django.db import models


class Migration(object):
    def forwards(self):
        db.add_column("dns_dnszoneprofile", "description", models.TextField("Description", blank=True, null=True))

    def backwards(self):
        db.delete_column("dns_dnszoneprofile", "description")
