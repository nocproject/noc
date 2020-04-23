# ----------------------------------------------------------------------
# managedobjectselector set vc_domain
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        return  # Conflicts with 0087_managedobjectselector_managed, skip
