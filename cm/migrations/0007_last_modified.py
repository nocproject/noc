# ----------------------------------------------------------------------
# last modified
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import stat
import datetime

# Third-party modules
from django.db import models

# NOC modules
from noc.config import config
from noc.core.migration.base import BaseMigration

TYPES = {"config": "config", "prefixlist": "prefix-list", "dns": "dns", "rpsl": "rpsl"}


class Migration(BaseMigration):
    def migrate(self):
        repo_root = config.path.repo
        for ot in TYPES:
            self.db.add_column(
                "cm_%s" % ot,
                "last_modified",
                models.DateTimeField("Last Modified", blank=True, null=True),
            )
            if repo_root:
                repo = os.path.join(repo_root, TYPES[ot])
                for id, repo_path in self.db.execute("SELECT id,repo_path FROM cm_%s" % ot):
                    path = os.path.join(repo, repo_path)
                    if os.path.exists(path):
                        lm = datetime.datetime.fromtimestamp(os.stat(path)[stat.ST_MTIME])
                        self.db.execute(
                            "UPDATE cm_%s SET last_modified=%%s WHERE id=%%s" % ot, [lm, id]
                        )
