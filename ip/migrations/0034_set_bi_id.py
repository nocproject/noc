# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# set bi_id
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# NOC modules
from noc.core.handler import get_handler


class Migration(object):
    def forwards(self):
        fix = get_handler("noc.fixes.fix_bi_id.fix")
        if fix:
            fix()

    def backwards(self):
        pass
