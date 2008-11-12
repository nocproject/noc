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
        
        args=[Settings.get("shell.pg_dump"),"-Fc"]
        if settings.DATABASE_USER:
            args+=["-U '%s'"%settings.DATABASE_USER]
        #if settings.DATABASE_PASSWORD:
        #    args+=["-W"]
        if settings.DATABASE_HOST:
            args+=["-h '%s'"%settings.DATABASE_HOST]
        if settings.DATABASE_PORT:
            args+=["-p '%s'"%settings.DATABASE_PORT]
        args+=["'%s'"%settings.DATABASE_NAME]
        now=datetime.datetime.now()
        out="noc-%04d-%02d-%02d-%02d-%02d.dump"%(now.year,now.month,now.day,now.hour,now.minute)
        out=os.path.join(Settings.get('main.backup_dir'),out)
        logging.debug("main.backup: dumping into %s"%out)
        cmd=" ".join(args)+" > "+"'%s'"%out
        p=subprocess.Popen(cmd,shell=True)
        pid,status=os.waitpid(p.pid,0)
        return status==0
