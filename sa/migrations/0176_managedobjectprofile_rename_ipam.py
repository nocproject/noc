# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Rename fields
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from south.db import db


class Migration(object):
    def forwards(self):
        db.execute("""
          ALTER TABLE sa_managedobjectprofile 
          RENAME enable_box_discovery_address 
          TO enable_box_discovery_address_neighbor""")
        db.execute("""
          ALTER TABLE sa_managedobjectprofile 
          RENAME enable_box_discovery_prefix 
          TO enable_box_discovery_prefix_neighbor""")

    def backwards(self):
        pass
