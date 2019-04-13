# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# terminationgroup tags
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db
# NOC modules
from noc.core.model.fields import TagsField


class Migration(object):
    def forwards(self):
        db.add_column("sa_terminationgroup", "tags", TagsField("Tags", null=True, blank=True))

    def backwards(self):
        pass
