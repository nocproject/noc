# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Create default user
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


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
                "admin",
                "NOC",
                "Admin",
                "test@example.com",
                "sha1$235c1$e8e4d9aaa945e1fae62a965ee87fbf7b4a185e3f",
                True,
                True,
            ],
        )
