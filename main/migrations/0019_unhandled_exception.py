# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# unhandled exception
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
        if db.execute("SELECT COUNT(*) FROM main_systemnotification WHERE name=%s",
                      ["main.unhandled_exception"])[0][0] == 0:
            db.execute("INSERT INTO main_systemnotification(name) VALUES(%s)", ["main.unhandled_exception"])

    def backwards(self):
        pass
