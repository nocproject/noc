# ----------------------------------------------------------------------
# managedobject attribute
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
        ManagedObject = self.db.mock_model(
            model_name="ManagedObject",
            db_table="sa_managedobject"
        )

        # Model "MapTask"
        self.db.create_table(
            "sa_managedobjectattribute", (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("managed_object", models.ForeignKey(ManagedObject, verbose_name="Managed Object", on_delete=models.CASCADE)),
                ("key", models.CharField("Key", max_length=64)),
                ("value", models.CharField("Value", max_length=4096, blank=True, null=True))
            )
        )
        self.db.create_index("sa_managedobjectattribute", ["managed_object_id", "key"], unique=True)
