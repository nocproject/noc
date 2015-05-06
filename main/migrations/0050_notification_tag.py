# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main_notification.tag field
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## Third-party modules
from south.db import db


class Migration:
    def forwards(self):
        db.add_column(
            "main_notification", "tag",
            models.CharField("Tag", max_length=256,
                             db_index=True, null=True, blank=True))

    def backwards(self):
        db.drop_column("main_notification", "tag")
