# ----------------------------------------------------------------------
# migrate tags
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.model.fields import TagsField
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    TAG_MODELS = ["dns_dnszone", "dns_dnszonerecord"]

    def migrate(self):
        # Create temporary tags fields
        for m in self.TAG_MODELS:
            self.db.add_column(m, "tmp_tags", TagsField("Tags", null=True, blank=True))
        # Migrate data
        for m in self.TAG_MODELS:
            self.db.execute(
                """
            UPDATE %s
            SET tmp_tags = string_to_array(regexp_replace(tags, ',$', ''), ',')
            WHERE tags != ''
            """
                % m
            )
