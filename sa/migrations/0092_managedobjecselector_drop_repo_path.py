# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from south.db import db


class Migration:

    def forwards(self):
        db.drop_column("sa_managedobjectselector", "filter_repo_path")

    def backwards(self):
        """Write your backwards migration here"""
