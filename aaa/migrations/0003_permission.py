# ----------------------------------------------------------------------
# permission
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
        if self.db.has_table("main_permission"):
            # Already created for elder installations
            return
        # Adding model "Permission"
        self.db.create_table(
            "main_permission",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("Name", max_length=128, unique=True)),
            ),
        )
        Permission = self.db.mock_model(model_name="Permission", db_table="main_permission")

        # Adding ManyToManyField "Permission.groups"
        Group = self.db.mock_model(model_name="Group", db_table="auth_group")
        self.db.create_table(
            "main_permission_groups",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("permission", models.ForeignKey(Permission, null=False, on_delete=models.CASCADE)),
                ("group", models.ForeignKey(Group, null=False, on_delete=models.CASCADE)),
            ),
        )

        # Adding ManyToManyField "Permission.users"
        User = self.db.mock_model(model_name="User", db_table="auth_user")
        self.db.create_table(
            "main_permission_users",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("permission", models.ForeignKey(Permission, null=False, on_delete=models.CASCADE)),
                ("user", models.ForeignKey(User, null=False, on_delete=models.CASCADE)),
            ),
        )
