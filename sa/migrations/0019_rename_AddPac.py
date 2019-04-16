# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# rename AddPac
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
        db.execute("UPDATE sa_managedobject SET profile_name='AddPac.APOS' WHERE profile_name='VoiceFinder.AddPack'")

    def backwards(self):
        db.execute("UPDATE sa_managedobject SET profile_name='VoiceFinder.AddPack' WHERE profile_name='AddPac.APOS'")
