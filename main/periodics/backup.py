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
import os,subprocess,datetime
import logging

class Task(noc.sa.periodic.Task):
    name="main.backup"
    description=""
    
    def execute(self):
        def safe_unlink(path):
            logging.debug("Unlinking: %s"%path)
            try:
                os.unlink(path)
            except:
                pass
        from django.conf import settings
        # Build backup path
        now=datetime.datetime.now()
        out="noc-%04d-%02d-%02d-%02d-%02d.dump"%(now.year,now.month,now.day,now.hour,now.minute)
        out=os.path.join(config.get("path","backup_dir"),out)
        # Build pg_dump command and options
        cmd=[config.get("path","pg_dump"),"-Fc"]
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
        # Launch pg_dump
        logging.info("main.backup: dumping database into %s"%out)
        retcode=subprocess.call(cmd)
        if retcode!=0:
            logging.error("main.backup: dump failed. Removing broken dump '%s'"%out)
            safe_unlink(out)
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
        #logging.error("main.backup: repo dump failed. Removing broken dumps")
        #safe_unlink(repo_out)
