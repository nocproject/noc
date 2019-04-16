# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# remove dnszonerecordtype
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
        db.delete_column("dns_dnszonerecord", "type_id")
        db.drop_table("dns_dnszonerecordtype")

    def backwards(self):
        pass
