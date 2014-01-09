# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from south.db import db


class Migration:
    def forwards(self):
        db.execute("""
        DELETE FROM fm_eventtrigger
        WHERE pyrule_id IN (
            SELECT id FROM main_pyrule WHERE name = 'refresh_config'
        )
        """)

    def backwards(self):
        pass
