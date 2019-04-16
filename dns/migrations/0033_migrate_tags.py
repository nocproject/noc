# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# migrate tags
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
    TAG_MODELS = ["dns_dnszone", "dns_dnszonerecord"]

    def forwards(self):
        # Create temporary tags fields
        for m in self.TAG_MODELS:
            db.add_column(m, "tmp_tags", TagsField("Tags", null=True, blank=True))
        # Migrate data
        for m in self.TAG_MODELS:
            db.execute(
                """
            UPDATE %s
            SET tmp_tags = string_to_array(regexp_replace(tags, ',$', ''), ',')
            WHERE tags != ''
            """ % m
            )

    def backwards(self):
        pass
