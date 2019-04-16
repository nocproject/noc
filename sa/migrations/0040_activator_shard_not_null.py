# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# activator shard not null
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
        db.execute("ALTER TABLE sa_activator ALTER shard_id SET NOT NULL")

    def backwards(self):
        pass
