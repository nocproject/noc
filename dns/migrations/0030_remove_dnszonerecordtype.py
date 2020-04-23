# ----------------------------------------------------------------------
# remove dnszonerecordtype
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.delete_column("dns_dnszonerecord", "type_id")
        self.db.delete_table("dns_dnszonerecordtype")
