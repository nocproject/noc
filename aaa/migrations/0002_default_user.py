# ----------------------------------------------------------------------
# Create default user
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.password.hasher import make_password
from noc.config import config


class Migration(BaseMigration):
    def migrate(self):
        # Create default admin user if no user exists
        if not self.db.execute("SELECT COUNT(*) FROM auth_user")[0][0] == 0:
            return
        self.db.execute(
            "INSERT INTO auth_user"
            "(username, first_name, last_name, email, password, is_active, is_superuser, date_joined) "
            "VALUES(%s, %s, %s, %s, %s, %s, %s, 'now')",
            [
                config.initial.admin_user_name,
                "NOC",
                "Admin",
                config.initial.admin_email,
                make_password(config.initial.admin_password),
                True,
                True,
            ],
        )
