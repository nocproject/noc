##
## Backup database to main.backupdir
## TODO:
##      * Remove backup when pg_dump failed
##      * Provide pg_dump with password when requred
##      * Remove old dumps
##
import noc.sa.periodic
import os,subprocess,datetime
import logging

class Task(noc.sa.periodic.Task):
    name="main.backup"
    description=""
    
    def execute(self):
        from noc.setup.models import Settings
        from django.conf import settings
        
        now=datetime.datetime.now()
        cmd=[Settings.get("shell.pg_dump"),"-Fc"]
        out="noc-%04d-%02d-%02d-%02d-%02d.dump"%(now.year,now.month,now.day,now.hour,now.minute)
        out=os.path.join(Settings.get('main.backup_dir'),out)
        cmd+=["-f",out]
        if settings.DATABASE_USER:
            cmd+=["-U",settings.DATABASE_USER]
        #if settings.DATABASE_PASSWORD:
        #    cmd+=["-W"]
        if settings.DATABASE_HOST:
            cmd+=["-h",settings.DATABASE_HOST]
        if settings.DATABASE_PORT:
            cmd+=["-p",str(settings.DATABASE_PORT)]
        cmd+=[settings.DATABASE_NAME]

        logging.debug("main.backup: dumping into %s"%out)
        p=subprocess.Popen(cmd)
        pid,status=os.waitpid(p.pid,0)
        if status!=0:
            logging.error("main.backup: dump failed. Removing broken dump '%s'"%out)
            # Remove broken dump
            try:
                os.unlink(out)
            except:
                pass
        return status==0
