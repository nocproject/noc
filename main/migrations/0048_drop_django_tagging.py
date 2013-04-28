# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Drop django-tagging tables
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from south.db import db


class Migration:
    def forwards(self):
        db.drop_table("tagging_taggeditem")
        db.drop_table("tagging_tag")

    def backwards(self):
        pass
