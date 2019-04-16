# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# lowercase stencil filenames
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db


class Migration(object):
    def forwards(self):
        db.execute(
            """update sa_managedobjectprofile
            set shape=upper(substring(shape from 1 for 1))||lower(substring(shape from 2 for length(shape)))"""
        )
        db.execute(
            """update sa_managedobject
            set shape=upper(substring(shape from 1 for 1))||lower(substring(shape from 2 for length(shape)))"""
        )

    def backwards(self):
        pass
