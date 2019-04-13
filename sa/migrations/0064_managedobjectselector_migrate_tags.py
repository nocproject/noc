# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobjectselector migrate tags
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
        # Create temporary tags fields
        db.add_column("sa_managedobjectselector", "tmp_filter_tags", TagsField("Tags", null=True, blank=True))
        # Migrate data
        db.execute(
            """
            UPDATE sa_managedobjectselector
            SET tmp_filter_tags = string_to_array(regexp_replace(filter_tags, ',$', ''), ',')
            WHERE filter_tags != ''
            """
        )

    def backwards(self):
        pass
