# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Backup database to main.backupdir
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
        
        now=datetime.datetime.now()
        cmd=[config.get("path","pg_dump"),"-Fc"]
        out="noc-%04d-%02d-%02d-%02d-%02d.dump"%(now.year,now.month,now.day,now.hour,now.minute)
        out=os.path.join(config.get("path","backup_dir"),out)
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

        logging.info("main.backup: dumping database into %s"%out)
        retcode=subprocess.call(cmd)
        if retcode!=0:
            logging.error("main.backup: dump failed. Removing broken dump '%s'"%out)
            safe_unlink(out)
            return False
        repo_root=config.get("cm","repo")
        repo_out="noc-%04d-%02d-%02d-%02d-%02d.tar"%(now.year,now.month,now.day,now.hour,now.minute)
        repo_out=os.path.join(config.get("path","backup_dir"),repo_out)
        cmd=["/usr/bin/tar","cf",repo_out]+[f for f in os.listdir(repo_root) if not f.startswith(".")]
        # Dumping repo
        logging.info("main.backup: dumping repo into %s"%repo_out)
        retcode=subprocess.call(cmd,cwd=repo_root)
        if retcode!=0:
            logging.error("main.backup: repo dump failed. Removing broken dumps")
            safe_unlink(out)
            safe_unlink(repo_out)
            return False
        cmd=["/usr/bin/gzip",repo_out]
        logging.info("main.backup: gzipping repo dump")
        retcode=subprocess.call(cmd)
        if retcode!=0:
            logging.error("main.backup: repo dump gzip failed. Removing broken dumps")
            safe_unlink(out)
            safe_unlink(repo_out)
            return False
        return True
