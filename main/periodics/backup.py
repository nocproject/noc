# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Backup database and repo to main.backupdir
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.periodic
from noc.settings import config
from noc.lib.fileutils import safe_rewrite
import os,subprocess,datetime,re
import logging

rx_backup=re.compile(r"^noc-(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})-\d{2}-\d{2}.(?:dump|tar\.gz)$")

class Task(noc.sa.periodic.Task):
    name="main.backup"
    description=""
    
    def clean_backups(self):
        backup_dir=config.get("path","backup_dir")
        keep_days=config.getint("backup","keep_days")
        keep_weeks=config.getint("backup","keep_weeks")
        keep_day_of_week=config.getint("backup","keep_day_of_week")
        keep_months=config.getint("backup","keep_months")
        keep_day_of_month=config.getint("backup","keep_day_of_month")
        
        now=datetime.datetime.now()
        for f in os.listdir(backup_dir):
            match=rx_backup.match(f)
            if not match:
                continue
            try:
                bdate=datetime.datetime(year=int(match.group("year")),month=int(match.group("month")),day=int(match.group("day")))
            except:
                continue
            # Filter out actual backups
            delta=now-bdate
            if delta.days<keep_days:
                continue
            elif delta.days<keep_days+keep_weeks*7:
                if bdate.weekday()==keep_day_of_week or bdate.day==keep_day_of_month:
                    continue
            elif delta.days<keep_days+keep_weeks*7+keep_months*31:
                if bdate.day==keep_day_of_month:
                    continue
            # Remove deprecated backups
            logging.info("Removing obsolete backup %s"%f)
            self.safe_unlink(os.path.join(backup_dir,f))
            
    def safe_unlink(self,path):
        logging.debug("Unlinking: %s"%path)
        try:
            os.unlink(path)
        except:
            pass
            
    def execute(self):
        def pgpass_quote(s):
            return s.replace("\\","\\\\").replace(":","\\:")
        from django.conf import settings
        # Clean up old backups
        self.clean_backups()
        # Build backup path
        now=datetime.datetime.now()
        pgpass=["*","*","*","*",""] # host,port,database,user,password
        out="noc-%04d-%02d-%02d-%02d-%02d.dump"%(now.year,now.month,now.day,now.hour,now.minute)
        out=os.path.join(config.get("path","backup_dir"),out)
        # Build pg_dump command and options
        cmd=[config.get("path","pg_dump"),"-Fc"]
        cmd+=["-f",out]
        if settings.DATABASE_USER:
            cmd+=["-U",settings.DATABASE_USER]
            pgpass[3]=settings.DATABASE_USER
        if settings.DATABASE_PASSWORD:
            pgpass[4]=settings.DATABASE_PASSWORD
        if settings.DATABASE_HOST:
            cmd+=["-h",settings.DATABASE_HOST]
            pgpass[0]=settings.DATABASE_HOST
        if settings.DATABASE_PORT:
            cmd+=["-p",str(settings.DATABASE_PORT)]
            pgpass[1]=settings.DATABASE_PORT
        cmd+=[settings.DATABASE_NAME]
        pgpass[2]=settings.DATABASE_NAME
        # Create temporary .pgpass
        pgpass_data=":".join([pgpass_quote(x) for x in pgpass])
        pgpass_path=os.path.join(os.getcwd(),"local","cache","pgpass",".pgpass")
        safe_rewrite(pgpass_path,pgpass_data,mode=0600)
        env=os.environ.copy()
        env["PGPASSFILE"]=pgpass_path
        # Launch pg_dump
        logging.info("main.backup: dumping database into %s"%out)
        retcode=subprocess.call(cmd,env=env)
        if retcode!=0:
            logging.error("main.backup: dump failed. Removing broken dump '%s'"%out)
            self.safe_unlink(out)
            return False
        #
        # Back up repo
        #
        repo_root=config.get("cm","repo")
        repo_out="noc-%04d-%02d-%02d-%02d-%02d.tar.gz"%(now.year,now.month,now.day,now.hour,now.minute)
        repo_out=os.path.join(config.get("path","backup_dir"),repo_out)
        logging.info("main.backup: dumping repo into %s"%repo_out)
        tar_cmd=[config.get("path","tar"),"cf","-"]+[f for f in os.listdir(repo_root) if not f.startswith(".")]
        gzip_cmd=[config.get("path","gzip")]
        f=open(repo_out,"w")
        p1=subprocess.Popen(tar_cmd,cwd=repo_root,stdout=subprocess.PIPE)
        p2=subprocess.Popen(gzip_cmd,stdin=p1.stdout,stdout=f)
        f.close()
        return True
