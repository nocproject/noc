# ----------------------------------------------------------------------
# Reset Project.shape_overlay_glyph
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self) -> None:
        self.db.execute("UPDATE project_project SET shape_overlay_glyph = NULL")
