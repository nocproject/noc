# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# no lg
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
        db.delete_table('peer_lgquerycommand')
        db.delete_table('peer_lgquerytype')

    def backwards(self):
        pass
