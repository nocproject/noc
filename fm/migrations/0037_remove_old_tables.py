# ----------------------------------------------------------------------
# remove old tables
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.delete_table("fm_eventrepeat")
        self.db.delete_table("fm_eventlog")
        self.db.delete_table("fm_eventdata")
        self.db.delete_table("fm_event")
        self.db.delete_table("fm_mibdata")
        self.db.delete_table("fm_mibdependency")
        self.db.delete_table("fm_mib")
        self.db.delete_table("fm_eventpriority")
        self.db.delete_table("fm_eventpostprocessingre")
        self.db.delete_table("fm_eventpostprocessingrule")
        self.db.delete_table("fm_eventcorrelationmatchedvar")
        self.db.delete_table("fm_eventcorrelationmatchedclass")
        self.db.delete_table("fm_eventclassificationre")
        self.db.delete_table("fm_eventclassificationrule")
        self.db.delete_table("fm_eventclassvar")
        self.db.delete_table("fm_eventclass")
        self.db.delete_table("fm_eventcategory")
