# ----------------------------------------------------------------------
# pyrule
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("main", "0022_pyrule_is_builtin")]

    def migrate(self):
        PyRule = self.db.mock_model(model_name="PyRule", db_table="main_pyrule")
        self.db.add_column(
            "fm_eventclass",
            "rule",
            models.ForeignKey(
                PyRule, verbose_name="pyRule", null=True, blank=True, on_delete=models.CASCADE
            ),
        )
        self.db.add_column(
            "fm_eventpostprocessingrule",
            "rule",
            models.ForeignKey(
                PyRule, verbose_name="pyRule", null=True, blank=True, on_delete=models.CASCADE
            ),
        )
        self.db.delete_column("fm_eventclass", "trigger")
