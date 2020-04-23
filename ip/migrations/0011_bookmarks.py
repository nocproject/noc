# ----------------------------------------------------------------------
# bookmarks
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        IPv4Block = self.db.mock_model(model_name="IPv4Block", db_table="ip_ipv4block")
        User = self.db.mock_model(model_name="User", db_table="auth_user")
        # Adding model 'IPv4BlockBookmark'
        self.db.create_table(
            "ip_ipv4blockbookmark",
            (
                ("id", models.AutoField(primary_key=True)),
                ("user", models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)),
                (
                    "prefix",
                    models.ForeignKey(IPv4Block, verbose_name="Prefix", on_delete=models.CASCADE),
                ),
            ),
        )

        # Creating unique_together for [user,prefix]
        self.db.create_index("ip_ipv4blockbookmark", ["user_id", "prefix_id"], unique=True)
