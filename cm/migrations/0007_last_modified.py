
from south.db import db
from noc.cm.models import *
import os,stat,datetime

TYPES={
    "config":"config",
    "prefixlist":"prefix-list",
    "dns":"dns",
    "rpsl":"rpsl",
    }

class Migration:
    def get_repo(self):
        l=db.execute("SELECT value FROM setup_settings WHERE key=%s",["cm.repo"])
        if len(l)!=1:
            return None
        else:
            return l[0][0]
        
    def forwards(self):
        repo_root=self.get_repo()
        for ot in TYPES:
            db.add_column("cm_%s"%ot,"last_modified",models.DateTimeField("Last Modified",blank=True,null=True))
            if repo_root:
                repo=os.path.join(repo_root,TYPES[ot])
                for id,repo_path in db.execute("SELECT id,repo_path FROM cm_%s"%ot):
                    path=os.path.join(repo,repo_path)
                    if os.path.exists(path):
                        lm=datetime.datetime.fromtimestamp(os.stat(path)[stat.ST_MTIME])
                        db.execute("UPDATE cm_%s SET last_modified=%%s WHERE id=%%s"%ot,[lm,id])
    
    def backwards(self):
        for ot in TYPES:
            db.delete_column("cm_%s"%ot,"last_modified")
