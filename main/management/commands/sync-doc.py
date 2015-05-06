# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Rebuild online documentation
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
from __future__ import with_statement
import os
import glob
import subprocess
import csv
import cStringIO
import sys
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.lib.fileutils import rewrite_when_differ

INIT = "__init__.py"


##
## Command handler
##
class Command(BaseCommand):
    help = "Synchronize online documentation"
    
    ##
    ## Rebuild supported equipment database.
    ## Returns true if database was updated
    ##
    def update_se_db(self):
        out = cStringIO.StringIO()
        writer = csv.writer(out)
        for dirpath, dirname, files in os.walk("sa/profiles/"):
            if "supported.csv" in files:
                pp = dirpath.split(os.path.sep)
                profile = "%s.%s" % (pp[-2], pp[-1])
                with open(os.path.join(dirpath, "supported.csv")) as f:
                    r = []
                    for row in csv.reader(f):
                        if len(row) != 3:
                            continue
                        vendor, model, version = row
                        m = "%s %s" % (vendor, model)
                        r += [(profile, m, version)]
                    for r in sorted(r):
                        writer.writerow(r)
        db_path = "local/supported.csv"
        return rewrite_when_differ(db_path, out.getvalue())
    
    ##
    ## Returns a list of distribution files
    ##
    def get_manifest(self):
        if os.path.exists(".hg"):
            # Repo found
            proc = subprocess.Popen(["hg", "locate"], stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            mf = stdout.splitlines()
        elif os.path.exists("MANIFEST"):
            with open("MANIFEST") as f:
                mf = f.read().splitlines()
        else:
            raise CommandError("Cannot find manifest")
        return mf
    
    ##
    ## Update "code's" index files
    ##
    def update_code_toc(self, root):
        def to_ignore(f):
            p = f.split(os.sep)
            if p[0] != INIT and len(p) == 1:
                return True
            if "tests" in p:
                return True
            if len(p) > 1 and p[1] in ("management", "migrations"):
                return True
            if len(p) > 1 and p[0] == "main" and p[1] == "pyrules":
                return True
            if len(p) > 1 and p[0] == "fm" and p[1] == "rules":
                return True
            if len(p) > 1 and p[0] == ("scripts", "share"):
                return True
            return False
        
        def header(h, level=0):
            return h + "\n" + ["=", "-", "~"][level] * len(h) + "\n"
        
        def path_to_mod(f):
            " Convert file path to module name"
            if f.endswith(INIT):
                f = f[:-12]
            else:
                f = f[:-3]
            return "noc." + f.replace(os.sep, ".")
        
        def path_to_doc(f):
            " Convert path fo RST file name"
            if f == INIT:
                return "index.rst"
            return path_to_mod(f) + ".rst"
        
        def package_doc(f):
            " Generate package doc"
            m = path_to_mod(f)
            r = header(":mod:`%s` Package" % m)
            r += ".. automodule:: %s\n    :members:\n\n" % m
            sp = package_files(f)
            if sp:
                r += header("Subpackages", 1)
                r += ".. toctree::\n    :maxdepth: 1\n\n"
                for t in sp:
                    r += "    %s\n" % path_to_mod(t)
            return r
        
        def module_doc(f):
            "Generate module doc"
            m = path_to_mod(f)
            r = header(":mod:`%s` Module" % m)
            r += ".. automodule:: %s\n    :members:\n\n" % m
            return r
        
        def package_files(f):
            " Return a list of package files"
            def is_child(ff):
                pp = ff.split(os.sep)
                if pp[-1] == INIT and len(pp) == lp + 2 and pp[:-2] == p:
                    return True
                if len(pp) != lp + 1:
                    return False
                return pp[:-1] == p
            
            p = f.split(os.sep)[:-1]
            lp = len(p)
            return sorted([ff for ff in dist if ff != f and is_child(ff)])
        
        def create_doc(f):
            if f.endswith(INIT):
                d = package_doc(f)
            else:
                d = module_doc(f)
            p = path_to_doc(f)
            rewrite_when_differ(os.path.join(root, p), d)
        
        dist = sorted([f for f in self.get_manifest()
                       if f.endswith(".py") and not to_ignore(f)])
        for f in dist:
            create_doc(f)
    
    ##
    ##
    ##
    def handle(self, *args, **options):
        #
        se_db_updated = self.update_se_db()
        # Prepare options
        opts = []
        if se_db_updated:
            opts += ["-a"]
        docset = set(args)
        # Prepare environment
        env = os.environ.copy()
        env["PYTHONPATH"] = ":".join(sys.path)
        env["PATH"] = os.path.abspath(os.path.join("contrib", "bin")) + ":" + env["PATH"]
        # Rebuild all documentation
        for conf in glob.glob("share/docs/*/*/conf.py"):
            d, f = os.path.split(conf)
            dn = d.split(os.sep)
            if docset and dn[-1] not in docset:
                continue
            if dn[-1] == "code":
                self.update_code_toc(d)
            target = os.path.abspath(os.path.join(d, "..", "..", "..", "..",
                                            "static", "doc", dn[-2], dn[-1]))
            doctrees = os.path.join(target, "doctrees")
            html = os.path.join(target, "html")
            for p in [doctrees, html]:
                if not os.path.isdir(p):
                    try:
                        os.makedirs(p)
                    except OSError:
                        raise CommandError("Unable to create directory: %s" % p)
            cmd = ["sphinx-build"]
            cmd += opts
            cmd += ["-b", "html", "-d", doctrees, "-D",
                     "latex_paper_size=a4", ".", html]
            try:
                subprocess.call(cmd, cwd=d, env=env)
            except OSError:
                raise CommandError("sphinx-build not found")
