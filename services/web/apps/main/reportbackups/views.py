# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Backups Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
from noc.lib.app.simplereport import SimpleReport,Report
from config import config
import os,datetime,stat
from noc.core.translation import ugettext as _
#
#
#
class ReportBackups(SimpleReport):
    title = _("Backup Status")
    def get_data(self,**kwargs):
        data=[]
        bd=config.path.backup_dir
        if os.path.isdir(bd):
            r=[]
            for f in [f for f in os.listdir(bd) if f.startswith("noc-") and (f.endswith(".dump") or f.endswith(".tar.gz"))]:
                s=os.stat(os.path.join(bd,f))
                r.append([f,datetime.datetime.fromtimestamp(s[stat.ST_MTIME]),s[stat.ST_SIZE]])
            data=sorted(r,lambda x,y:cmp(x[1],y[1]))
        return self.from_dataset(title=self.title,columns=["File","Size"],data=data)
