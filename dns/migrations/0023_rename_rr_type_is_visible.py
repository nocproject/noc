# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
=======
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
"""
"""
from south.db import db


class Migration:
    def forwards(self):
        db.rename_column("dns_dnszonerecordtype", "is_visible",
            "is_active")

    def backwards(self):
        db.rename_column("dns_dnszonerecordtype", "is_active",
            "is_visible")
