# ---------------------------------------------------------------------
# Backups Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
import datetime
import stat
import operator

# NOC modules
from ..simplereport import SimpleReport
from noc.config import config
from noc.core.translation import ugettext as _


class ReportBackups(SimpleReport):
    title = _("Backup Status")
    columns = ["file", "datetime", "size"]

    def get_records(self, **kwargs):
        data = []
        bd = config.path.backup_dir
        print("bd", bd, type(bd))
        if os.path.isdir(bd):
            r = []
            for f in [
                f
                for f in os.listdir(bd)
                if f.startswith("noc-") and (f.endswith(".dump") or f.endswith(".tar.gz"))
            ]:
                s = os.stat(os.path.join(bd, f))
                r.append([f, datetime.datetime.fromtimestamp(s[stat.ST_MTIME]), s[stat.ST_SIZE]])
            data = list(sorted(r, key=operator.itemgetter(1)))
        print("data", data, type(data))
        return data
