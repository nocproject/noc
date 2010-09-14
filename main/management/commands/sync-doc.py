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
from django.core.management.base import BaseCommand,CommandError
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
        # Prepare paths
        sphinx_build=os.path.abspath(os.path.join("contrib","bin","sphinx-build"))
        if not os.path.exists(sphinx_build):
            raise CommandError("%s not found. Please rebuild contrib/"%sphinx_build)
        #
        se_db_updated=self.update_se_db()
        # Prepare options
        opts=[]
        if se_db_updated:
            opts+=["-a"]
        # Prepare environment
        env=os.environ.copy()
        env["PYTHONPATH"]=":".join(sys.path)
        # Rebuild all documentation
        for conf in glob.glob("share/docs/*/*/conf.py"):
            d,f=os.path.split(conf)
            dn=d.split(os.sep)
            target=os.path.abspath(os.path.join(d,"..","..","..","..","static","doc",dn[-2],dn[-1]))
            doctrees=os.path.join(target,"doctrees")
            html=os.path.join(target,"html")
            for p in [doctrees,html]:
                if not os.path.isdir(p):
                    try:
                        os.makedirs(p)
                    except OSError:
                        raise CommandError("Unable to create directory: %s"%p)
            cmd=[sphinx_build]+opts+["-b","html","-d",doctrees,"-D","latex_paper_size=a4",".",html]
            subprocess.call(cmd,cwd=d,env=env)
