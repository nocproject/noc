# ----------------------------------------------------------------------
# Reset .shape_overlay_glyph
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self) -> None:
        self.db.execute("UPDATE sa_managedobjectprofile SET shape_overlay_glyph = NULL")
        self.db.execute("UPDATE sa_managedobject SET shape_overlay_glyph = NULL")
