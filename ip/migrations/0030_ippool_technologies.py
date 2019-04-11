# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ippool technologies
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db
from noc.core.model.fields import TextArrayField


class Migration(object):
    def forwards(self):
        db.add_column("ip_ippool", "technologies", TextArrayField("Technologies", default=["IPoE"]))

    def backwards(self):
        db.drop_column("ip_ippool", "technologies")
