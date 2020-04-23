# ----------------------------------------------------------------------
# managedobjectselector migrate tags
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.model.fields import TagsField


class Migration(BaseMigration):
    def migrate(self):
        # Create temporary tags fields
        self.db.add_column(
            "sa_managedobjectselector", "tmp_filter_tags", TagsField("Tags", null=True, blank=True)
        )
        # Migrate data
        self.db.execute(
            """
            UPDATE sa_managedobjectselector
            SET tmp_filter_tags = string_to_array(regexp_replace(filter_tags, ',$', ''), ',')
            WHERE filter_tags != ''
            """
        )
