from noc.main.report import Column
from noc.setup.models import Settings
import noc.main.report
import os,stat,datetime

class Report(noc.main.report.Report):
    name="main.backups"
    title="Backups Status"
    requires_cursor=False
    columns=[
        Column("File"),
        Column("Date Created"),
        Column("Size (bytes)",align="RIGHT")
    ]
    def get_queryset(self):
        bd=Settings.get("main.backup_dir")
        if not os.path.isdir(bd):
            return []
        r=[]
        for f in [f for f in os.listdir(bd) if f.startswith("noc-") and f.endswith(".dump")]:
            s=os.stat(os.path.join(bd,f))
            r.append([f,datetime.datetime.fromtimestamp(s[stat.ST_MTIME]),s[stat.ST_SIZE]])
        return sorted(r,lambda x,y:cmp(x[1],y[1]))