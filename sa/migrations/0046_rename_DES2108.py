# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# rename DES2108
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
        UPDATE sa_managedobject
        SET profile_name='DLink.DES21xx'
        WHERE profile_name='DLink.DES2108'"""
        )

    def backwards(self):
        db.execute(
            """
        UPDATE sa_managedobject
        SET profile_name='DLink.DES2108'
        WHERE profile_name='DLink.DES21xx'"""
        )
