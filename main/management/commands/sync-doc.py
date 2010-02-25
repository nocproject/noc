# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Rebuild online documentation
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
from django.core.management.base import BaseCommand
import os,glob,subprocess,csv,cStringIO,sys
from noc.lib.fileutils import rewrite_when_differ

##
## Command handler
##
class Command(BaseCommand):
    help="Syncronize online documentation"
    ##
    ## Rebuild supported equipment database.
    ## Returns true if database was updated
    ##
    def update_se_db(self):
        out=cStringIO.StringIO()
        writer=csv.writer(out)
        for dirpath,dirname,files in os.walk("sa/profiles/"):
            if "supported.csv" in files:
                pp=dirpath.split(os.path.sep)
                profile="%s.%s"%(pp[-2],pp[-1])
                with open(os.path.join(dirpath,"supported.csv")) as f:
                    r=[]
                    for row in csv.reader(f):
                        if len(row)!=3:
                            continue
                        vendor,model,version=row
                        m="%s %s"%(vendor,model)
                        r+=[(profile,m,version)]
                    for r in sorted(r):
                        writer.writerow(r)
        db_path="local/supported.csv"
        return rewrite_when_differ(db_path,out.getvalue())
        
    def handle(self, *args, **options):
        se_db_updated=self.update_se_db()
        # Find and build all makefiles
        for makefile in glob.glob("share/doc/index/Makefile")+glob.glob("share/doc/*/*/Makefile"):
            d,f=os.path.split(makefile)
            env=os.environ.copy()
            if se_db_updated:
                env["OPTIONS"]="-a"
            env["PYTHONPATH"]=":".join(sys.path)
            subprocess.call(["make","html"],cwd=d,env=env)
