# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from south.db import db
from django.db import models


class Migration:
    def forwards(self):
        db.add_column(
            "fm_eventtrigger",
            "handler",
            models.CharField(_("Handler"),
                             max_length=128, null=True, blank=True)
        )

    def backwards(self):
        db.drop_column("fm_eventtrigger", "handler")
