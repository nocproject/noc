# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from south.db import db


class Migration(object):
    def forwards(self):
        db.delete_table('peer_lgquerycommand')
        db.delete_table('peer_lgquerytype')

    def backwards(self):
        pass
