# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# default managedobjectprofile
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
        db.execute("""
        INSERT INTO sa_managedobjectprofile(name)
        VALUES('default')
        """)

    def backwards(self):
        pass
