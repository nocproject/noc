# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobjectprofile card title template
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db
from django.db import models


class Migration(object):
    def forwards(self):
        db.add_column(
            "sa_managedobjectprofile", "card_title_template",
            models.CharField(
                "Card title template", max_length=256, default="{{ object.object_profile.name }}: {{ object.name }}"
            )
        )

    def backwards(self):
        db.delete_column("sa_managedobjectprofile", "card")
