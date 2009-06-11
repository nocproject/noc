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
        def pgpass_quote(s):
            return s.replace("\\","\\\\").replace(":","\\:")
        from django.conf import settings
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
        print pgpass_data
        env=os.environ.copy()
        env["PGPASSFILE"]=pgpass_path
        # Launch pg_dump
        logging.info("main.backup: dumping database into %s"%out)
        retcode=subprocess.call(cmd,env=env)
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
