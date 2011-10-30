# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Static code analysys
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from __future__ import with_statement
from noc.settings import INSTALLED_APPS
from unittest import TestCase
import os,re

class CodeTest(TestCase):
    ##
    ## Returns a list of (module,symbols)
    ## with all import statements
    ##
    rx_import=re.compile(r"^(?:import\s+(\S+))|(?:from\s+(\S+)\s+import\s+(\S+(?:\s*,\S+)*))")
    def get_import_list(self,data):
        il=[]
        for l in data.splitlines():
            match=self.rx_import.search(l)
            if match:
                if match.group(1):
                    m=match.group(1)
                    symbols=[]
                else:
                    m=match.group(2)
                    symbols=[]
                    if match.group(3):
                        symbols=[s.strip() for s in match.group(3).split(",")]
                for x in [x.strip() for x in m.split(",")]:
                    il+=[(x,symbols)]
        return il
    ##
    ## Check every module with "with" statement
    ## has "from __future__ import with_statement"
    ##
    rx_with=re.compile(r"^\s*with\s+\S+")
    rx_ml_str = re.compile(r'""".*?"""', re.MULTILINE | re.DOTALL)
    def check_with(self,path,data):
        failures=[]
        # Check code has "with" statement
        has_with=False
        data = self.rx_ml_str.sub("", data)
        for l in data.splitlines():
            if self.rx_with.search(l):
                has_with=True
                break
        if has_with:
            # Check code has __future__ import for Python 2.5 compatibility
            has_future=False
            for mod,symbols in self.get_import_list(data):
                if mod=="__future__" and "with_statement" in symbols:
                    has_future=True
                    break
            if not has_future:
                failures+=["Error in %s: 'with' statement without __future__ import"%path]
        return failures
    ##
    ## Run tests for module
    ##
    def check_file(self,path,data):
        failures=self.check_with(path,data)
        return failures
    ##
    ## Test all modules
    ##
    def test_code(self):
        failures = []
        for d in [app[4:] for app in INSTALLED_APPS if app.startswith("noc.")]+["lib"]:
            for root, dirs, files in os.walk(d):
                if "templates" in root.split(os.sep):
                    continue
                for fn in [f for f in files if f.endswith(".py")]:
                    path = os.path.join(root,fn)
                    with open(os.path.join(root,fn)) as file:
                        failures += self.check_file(path,file.read())
        assert len(failures) == 0, "%d errors in code:\n\t" % len(failures) + "\n\t".join(failures)
