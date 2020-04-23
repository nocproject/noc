# ----------------------------------------------------------------------
# tags
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from noc.core.model.fields import AutoCompleteTagsField

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):

    TAG_MODELS = ["dns_dnszone", "dns_dnszonerecord"]

    def migrate(self):
        for m in self.TAG_MODELS:
            self.db.add_column(m, "tags", AutoCompleteTagsField("Tags", null=True, blank=True))
