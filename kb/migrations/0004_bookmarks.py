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
        # Mock Models
        KBEntry = self.db.mock_model(model_name="KBEntry", db_table="kb_kbentry")

        # Model "KBGlobalBookmark"
        self.db.create_table(
            "kb_kbglobalbookmark",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                (
                    "kb_entry",
                    models.ForeignKey(
                        KBEntry, verbose_name=KBEntry, unique=True, on_delete=models.CASCADE
                    ),
                ),
            ),
        )

        # Mock Models
        User = self.db.mock_model(model_name="User", db_table="auth_user")
        KBEntry = self.db.mock_model(model_name="KBEntry", db_table="kb_kbentry")

        # Model "KBUserBookmark"
        self.db.create_table(
            "kb_kbuserbookmark",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("user", models.ForeignKey(User, verbose_name=User, on_delete=models.CASCADE)),
                (
                    "kb_entry",
                    models.ForeignKey(KBEntry, verbose_name=KBEntry, on_delete=models.CASCADE),
                ),
            ),
        )
        self.db.create_index("kb_kbuserbookmark", ["user_id", "kb_entry_id"], unique=True)
