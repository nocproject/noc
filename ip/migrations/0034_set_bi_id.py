# ----------------------------------------------------------------------
# set bi_id
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.handler import get_handler
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        fix = get_handler("noc.fixes.fix_bi_id.fix")
        if fix:
            fix()
