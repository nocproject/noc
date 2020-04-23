# ----------------------------------------------------------------------
# lowercase stencil filenames
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.execute(
            """update sa_managedobjectprofile
            set shape=upper(substring(shape from 1 for 1))||lower(substring(shape from 2 for length(shape)))"""
        )
        self.db.execute(
            """update sa_managedobject
            set shape=upper(substring(shape from 1 for 1))||lower(substring(shape from 2 for length(shape)))"""
        )
