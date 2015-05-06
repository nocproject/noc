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
            "sa_objectnotification", "alarm_reopened",
            models.BooleanField("Alarm reopened", default=False))

    def backwards(self):
        db.drop_column("sa_objectnotification", "alarm_reopened")
