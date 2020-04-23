# ----------------------------------------------------------------------
# managedobjectprofile card title template
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
        self.db.add_column(
            "sa_managedobjectprofile",
            "card_title_template",
            models.CharField(
                "Card title template",
                max_length=256,
                default="{{ object.object_profile.name }}: {{ object.name }}",
            ),
        )
