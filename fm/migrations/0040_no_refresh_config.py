# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# no refresh config
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db


class Migration(object):
    def forwards(self):
        db.execute(
            """
        DELETE FROM fm_eventtrigger
        WHERE pyrule_id IN (
            SELECT id FROM main_pyrule WHERE name = 'refresh_config'
        )
        """
        )

    def backwards(self):
        pass
