# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# <describe module here>
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.handler import get_handler


class Migration(object):
    def forwards(self):
        fix = get_handler("noc.fixes.fix_bi_id.fix")
        if fix:
            fix()

    def backwards(self):
        pass
