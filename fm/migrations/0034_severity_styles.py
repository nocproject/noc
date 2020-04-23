# ----------------------------------------------------------------------
# severity styles
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # Create styles for alarm severities
        for name, font, background, description in [
            ("FM INFO", 12255232, 14480371, "Alarm severity INFO"),
            ("FM WARNING", 12255232, 16777181, "Alarm severity WARNING"),
            ("FM MINOR", 12255232, 16777147, "Alarm severity MINOR"),
            ("FM MAJOR", 12255232, 16772829, "Alarm severity MAJOR"),
            ("FM CRITICAL", 12255232, 16768460, "Alarm severity CRITICAL"),
        ]:
            if (
                self.db.execute("SELECT COUNT(*) FROM main_style WHERE name = %s", [name])[0][0]
                == 0
            ):
                self.db.execute(
                    "INSERT INTO main_style(name, font_color, background_color, description) VALUES (%s, %s, %s, %s)",
                    [name, font, background, description],
                )
