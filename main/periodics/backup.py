# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Backup database,  repo and configs to main.backupdir
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
from __future__ import with_statement
import os
import subprocess
import datetime
import re
import logging
## NOC modules
from noc.sa.periodic import Task as NOCTask
from noc.settings import config
from noc.lib.fileutils import safe_rewrite
##
## main.backup periodic task
##
class Task(NOCTask):
    name="main.backup"
    description=""
    
    ##
    ## Clean up obsolete backups
    ##
    rx_backup=re.compile(r"^noc-(?:(?:etc|repo|db)-)(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})-\d{2}-\d{2}.(?:dump|tar\.gz)$")
    def clean_backups(self):
        backup_dir=config.get("path", "backup_dir")
        keep_days=config.getint("backup", "keep_days")
        keep_weeks=config.getint("backup", "keep_weeks")
        keep_day_of_week=config.getint("backup", "keep_day_of_week")
        keep_months=config.getint("backup", "keep_months")
        keep_day_of_month=config.getint("backup", "keep_day_of_month")
        
        now=datetime.datetime.now()
        for f in os.listdir(backup_dir):
            match=self.rx_backup.match(f)
            if not match:
                continue
            try:
                bdate=datetime.datetime(year=int(match.group("year")), month=int(match.group("month")), day=int(match.group("day")))
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
            self.safe_unlink(os.path.join(backup_dir, f))
    
    ##
    ## Safely remove the file
    ##
    def safe_unlink(self, path):
        logging.debug("Unlinking: %s"%path)
        try:
            os.unlink(path)
        except:
            pass
    
    ##
    ## Create archive and append files
    ##
    def tar(self, archive, files, cwd=None):
        if not files:
            return
        tar_cmd=[config.get("path", "tar"), "cf", "-"]+files
        gzip_cmd=[config.get("path", "gzip")]
        logging.debug(("cd %s"%cwd if cwd else "")+" ".join(tar_cmd)+" | "+" ".join(gzip_cmd))
        with open(archive, "w") as f:
            p1=subprocess.Popen(tar_cmd, cwd=cwd, stdout=subprocess.PIPE)
            p2=subprocess.Popen(gzip_cmd, stdin=p1.stdout, stdout=f)
    
    ##
    ## Backup
    ##
    def execute(self):
        def pgpass_quote(s):
            return s.replace("\\", "\\\\").replace(":", "\\:")
        
        from django.conf import settings
        # Clean up old backups
        self.clean_backups()
        # Build backup path
        now=datetime.datetime.now()
        pgpass=["*", "*", "*", "*", ""] # host, port, database, user, password
        out="noc-db-%04d-%02d-%02d-%02d-%02d.dump"%(now.year, now.month, now.day, now.hour, now.minute)
        out=os.path.join(config.get("path", "backup_dir"), out)
        # Build pg_dump command and options
        cmd=[config.get("path", "pg_dump"), "-Fc"]
        cmd+=["-f", out]
        if settings.DATABASES["default"]["USER"]:
            cmd+=["-U", settings.DATABASES["default"]["USER"]]
            pgpass[3]=settings.DATABASES["default"]["USER"]
        if settings.DATABASES["default"]["PASSWORD"]:
            pgpass[4]=settings.DATABASES["default"]["PASSWORD"]
        if settings.DATABASES["default"]["HOST"]:
            cmd+=["-h", settings.DATABASES["default"]["HOST"]]
            pgpass[0]=settings.DATABASES["default"]["HOST"]
        if settings.DATABASES["default"]["PORT"]:
            cmd+=["-p", str(settings.DATABASES["default"]["PORT"])]
            pgpass[1]=settings.DATABASES["default"]["PORT"]
        cmd+=[settings.DATABASE_NAME]
        pgpass[2]=settings.DATABASE_NAME
        # Create temporary .pgpass
        pgpass_data=":".join([pgpass_quote(x) for x in pgpass])
        pgpass_path=os.path.join(os.getcwd(), "local", "cache", "pgpass", ".pgpass")
        safe_rewrite(pgpass_path, pgpass_data, mode=0600)
        env=os.environ.copy()
        env["PGPASSFILE"]=pgpass_path
        # Launch pg_dump
        logging.info("main.backup: dumping database into %s"%out)
        retcode=subprocess.call(cmd, env=env)
        if retcode!=0:
            logging.error("main.backup: dump failed. Removing broken dump %s"%out)
            self.safe_unlink(out)
            return False
        self.safe_unlink(pgpass_path) # Remove left pgpass
        #
        # Back up repo
        #
        repo_root=config.get("cm", "repo")
        repo_out="noc-repo-%04d-%02d-%02d-%02d-%02d.tar.gz"%(now.year, now.month, now.day, now.hour, now.minute)
        repo_out=os.path.join(config.get("path", "backup_dir"), repo_out)
        logging.info("main.backup: dumping repo into %s"%repo_out)
        self.tar(repo_out, [f for f in os.listdir(repo_root) if not f.startswith(".")], cwd=repo_root)
        #
        # Back up etc/
        #
        etc_out="noc-etc-%04d-%02d-%02d-%02d-%02d.tar.gz"%(now.year, now.month, now.day, now.hour, now.minute)
        etc_out=os.path.join(config.get("path", "backup_dir"), etc_out)
        logging.info("main.backup: dumping etc/ into %s"%etc_out)
        self.tar(etc_out, [os.path.join("etc", f) for f in os.listdir("etc") if f.endswith(".conf") and not f.startswith(".")])
        #
        return True
    
