# ----------------------------------------------------------------------
# Force to change default password
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.config import config
from noc.core.password.hasher import check_password


class Migration(BaseMigration):
    def migrate(self):
        r = self.db.execute("SELECT id, username, password, change_at FROM auth_user LIMIT 2")
        if len(r) != 1:
            return
        user_id, username, password, change_at = r[0]
        # Check username
        if username != config.initial.admin_user_name:
            return  # Username is already changed
        # Check password change schedule
        if change_at:
            return  # Already scheduled to change
        # Check password is not changed
        if not check_password(config.initial.admin_password, password):
            return  # Password is already changed
        # Schedule password change
        self.db.execute(
            "UPDATE auth_user SET change_at = %s WHERE id = %s", [datetime.datetime.now(), user_id]
        )
