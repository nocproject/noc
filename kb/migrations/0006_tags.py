# ----------------------------------------------------------------------
# tags
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.model.fields import AutoCompleteTagsField
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    TAG_MODELS = ["kb_kbentry", "kb_kbentrytemplate"]

    def migrate(self):
        for m in self.TAG_MODELS:
            self.db.add_column(m, "tags", AutoCompleteTagsField("Tags", null=True, blank=True))

    def backwards(self):
        for m in self.TAG_MODELS:
            self.db.delete_column(m, "tags")
