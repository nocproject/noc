# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# object_map drop
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# NOC models
from noc.lib.nosql import get_db


class Migration(object):
    def forwards(self):
        get_db().noc.cache.object_map.drop()

    def backwards(self):
        pass
