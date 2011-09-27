# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## Third-party modules
from south.db import db
## Python modules
from noc.fm.models import *


class Migration:    
    def forwards(self):
        # Create styles for alarm severities
        for name, font, background, description in [
            ("FM INFO", 12255232, 14480371, "Alarm severity INFO"),
            ("FM WARNING", 12255232, 16777181, "Alarm severity WARNING"),
            ("FM MINOR", 12255232, 16777147, "Alarm severity MINOR"),
            ("FM MAJOR", 12255232, 16772829, "Alarm severity MAJOR"),
            ("FM CRITICAL", 12255232, 16768460, "Alarm severity CRITICAL"),
        ]:
            if db.execute("SELECT COUNT(*) FROM main_style WHERE name = %s", [name])[0][0] == 0:
                db.execute("INSERT INTO main_style(name, font_color, background_color, description) VALUES (%s, %s, %s, %s)", [name, font, background, description])
    
    def backwards(self):
        db.execute("DELETE FROM main_style WHERE name LIKE 'FM %%'")
