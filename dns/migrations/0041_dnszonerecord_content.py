# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Enlarge DNSZoneRecord.content
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from south.db import db


class Migration(object):
    def forwards(self):
        db.execute("ALTER TABLE dns_dnszonerecord ALTER content TYPE VARCHAR(65536)")

    def backwards(self):
        pass
