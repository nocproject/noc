# ----------------------------------------------------------------------
# bi_id integer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.execute("UPDATE sa_managedobject SET bi_id=NULL")
        self.db.execute("ALTER TABLE sa_managedobject ALTER COLUMN bi_id TYPE bigint")
        self.db.execute("UPDATE sa_administrativedomain SET bi_id=NULL")
        self.db.execute("ALTER TABLE sa_administrativedomain ALTER COLUMN bi_id TYPE bigint")
        self.db.execute("UPDATE sa_authprofile SET bi_id=NULL")
        self.db.execute("ALTER TABLE sa_authprofile ALTER COLUMN bi_id TYPE bigint")
        self.db.execute("UPDATE sa_terminationgroup SET bi_id=NULL")
        self.db.execute("ALTER TABLE sa_terminationgroup ALTER COLUMN bi_id TYPE bigint")
        self.db.execute("UPDATE sa_managedobjectprofile SET bi_id=NULL")
        self.db.execute("ALTER TABLE sa_managedobjectprofile ALTER COLUMN bi_id TYPE bigint")
