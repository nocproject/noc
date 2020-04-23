# ---------------------------------------------------------------------
# reducetask script
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.execute("DELETE FROM sa_maptask")
        self.db.execute("DELETE FROM sa_reducetask")
        self.db.execute("COMMIT")
        self.db.add_column("sa_reducetask", "script", models.TextField("Script"))
        self.db.delete_column("sa_reducetask", "reduce_script")
