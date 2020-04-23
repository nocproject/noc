# ----------------------------------------------------------------------
# priority color
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
            "fm_eventpriority",
            "font_color",
            models.CharField("Font Color", max_length=32, blank=True, null=True),
        )
        self.db.add_column(
            "fm_eventpriority",
            "background_color",
            models.CharField("Background Color", max_length=32, blank=True, null=True),
        )
