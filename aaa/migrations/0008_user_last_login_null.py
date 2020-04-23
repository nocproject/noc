# ----------------------------------------------------------------------
# Set auth_user.last_login to NULLable
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        is_nullable = self.db.execute(
            """
            SELECT is_nullable = 'YES'
            FROM information_schema.columns
            WHERE
              table_name = 'auth_user'
              AND column_name = 'last_login'
            """
        )[0][0]
        if is_nullable:
            return
        self.db.execute(
            """
            ALTER TABLE auth_user
            ALTER last_login
            DROP NOT NULL
            """
        )
