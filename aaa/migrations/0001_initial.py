# ----------------------------------------------------------------------
# Create User and Group models
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python import datetime
import datetime

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # Elder installations has auth_user and auth_group tables
        # created by django"s auth application.
        # Skip if tables exists
        if self.db.has_table("auth_user"):
            # Enlarge username, django creates too short
            self.db.execute("ALTER TABLE auth_user ALTER username TYPE VARCHAR(75)")
            return
        # User model
        self.db.create_table(
            "auth_user",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("username", models.CharField(max_length=75, unique=True)),
                ("first_name", models.CharField(max_length=75, blank=True)),
                ("last_name", models.CharField(max_length=75, blank=True)),
                ("email", models.EmailField(blank=True)),
                ("password", models.CharField(max_length=128)),
                ("is_active", models.BooleanField(default=True)),
                ("is_superuser", models.BooleanField(default=False)),
                ("date_joined", models.DateTimeField(default=datetime.datetime.now)),
            ),
        )
        # Group model
        self.db.create_table(
            "auth_group",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField(max_length=80, unique=True)),
            ),
        )
        #
        # Adding ManyToManyField "User.groups"
        User = self.db.mock_model(model_name="User", db_table="auth_user")
        Group = self.db.mock_model(model_name="Group", db_table="auth_group")
        self.db.create_table(
            "auth_user_groups",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("user", models.ForeignKey(User, null=False, on_delete=models.CASCADE)),
                ("group", models.ForeignKey(Group, null=False, on_delete=models.CASCADE)),
            ),
        )
