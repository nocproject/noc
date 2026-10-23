# ----------------------------------------------------------------------
# Reset glyph collection
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [
        ("inv", "0044_reset_glyphs"),
        ("sa", "0269_reset_glyphs"),
        ("project", "0005_reset_glyphs"),
    ]

    def migrate(self) -> None:
        self.mongo_db["glyph"].drop()
