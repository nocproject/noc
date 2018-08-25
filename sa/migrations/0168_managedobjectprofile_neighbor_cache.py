# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ManagedObject.neighbor_cache_ttl
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from south.db import db
from django.db import models


class Migration(object):
    def forwards(self):
        db.add_column(
            "sa_managedobjectprofile",
            "neighbor_cache_ttl",
            models.IntegerField(
                "Neighbor Cache TTL",
                default=0
            )
        )

    def backwards(self):
        db.delete_column("sa_managedobjectprofile",
                         "neighbor_cache_ttl")
