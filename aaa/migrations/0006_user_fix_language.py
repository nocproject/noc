# ----------------------------------------------------------------------
# Fix User.preferred_language defaults
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # Set proper preferred language
        self.db.execute(
            """
            UPDATE auth_user
            SET preferred_language = %s
            WHERE preferred_language = %s
            """,
            ["en", "en-us"],
        )
        current_default = self.db.execute(
            """
            SELECT column_default
            FROM information_schema.columns
            WHERE
              table_name = 'auth_user'
              AND column_name='preferred_language'
            """
        )[0][0]
        # May return
        # 'en-us'::character varying
        if "en-us" in current_default:
            self.db.execute(
                """
                ALTER TABLE auth_user
                ALTER COLUMN preferred_language SET DEFAULT 'en'
                """
            )
