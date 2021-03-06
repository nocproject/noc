# ----------------------------------------------------------------------
# tags
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.model.fields import AutoCompleteTagsField


class Migration(BaseMigration):
    TAG_MODELS = ["sa_activator", "sa_managedobject"]

    def migrate(self):
        for m in self.TAG_MODELS:
            self.db.add_column(m, "tags", AutoCompleteTagsField("Tags", null=True, blank=True))
        self.db.add_column(
            "sa_managedobjectselector",
            "filter_tags",
            AutoCompleteTagsField("Tags", null=True, blank=True),
        )
