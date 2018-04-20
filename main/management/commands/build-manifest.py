# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Build MANIFEST
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.core.management.base import BaseCommand
import os,sys,re
##
## Do not forget to syncronize with .hgignore
##
EXCLUDE=[
    re.compile(r"\.pyc$"),
    re.compile(r"\.pyo$"),
    re.compile(r"\.swp$"),
    re.compile(r"^dist/"),
    re.compile(r"^build/"),
    re.compile(r"^noc\.egg-info/"),
    re.compile(r"^etc/[^/]+\.conf$"),
    re.compile(r"^etc/certs/"),
    re.compile(r"^local/"),
    re.compile(r"^static/doc/"),
    re.compile(r"^share/static/doc/(html|doctrees)/"),
    re.compile(r"^MANIFEST$"),
]

##
## build-manifest command handler
##
class Command(BaseCommand):
    help="Build MANIFEST"
    def handle(self, *args, **options):
        r=[]
        prefix=os.path.dirname(sys.argv[0])
        if not prefix:
            prefix="."
        for dirpath,dirnames,filenames in os.walk(prefix):
            if dirpath.startswith("./.hg"):
                continue
            for f in filenames:
                path=os.path.join(dirpath,f)
                if path.startswith("./"):
                    path=path[2:]
                if path.startswith(".hg"):
                    continue
                ignore=False
                for e in EXCLUDE:
                    if e.search(path):
                        ignore=True
                        break
                if ignore:
                    continue
                r.append(path)
        print "\n".join(sorted(r))
