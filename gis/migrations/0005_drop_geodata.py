# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from south.db import db


class Migration(object):
    def forwards(self):
        db.drop_table("gis_geodata")

    def backwards(self):
        pass
