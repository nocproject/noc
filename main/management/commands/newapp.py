# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Create application skeleton
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import os
import datetime
from optparse import make_option
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.settings import INSTALLED_APPS


class Command(BaseCommand):
    """
    Create and initialize appliation skeleton
    """
    help = "Create application skeleton"
    option_list=BaseCommand.option_list+(
        make_option("--model", "-m", dest="model",
                    help="Create ModelApplication"),
        make_option("--report", "-r", dest="report",
                    choices=["simple"],
                    help="Create Report"))

    def create_dir(self, path):
        print "    Creating directory %s ..." % path,
        try:
            os.mkdir(path)
            print "done"
        except OSError, why:
            print "failed:", why
            raise CommandError("Failed to create directory")

    def create_file(self, path, data):
        print "    Writing file %s ..." % path,
        try:
            with open(path, "w") as f:
                f.write(data)
            print "done"
        except OSError, why:
            print "failed:", why
            raise CommandError("Failed to write file")

    def handle(self, *args, **options):
        # Template variables
        vars = {
            "year": str(datetime.datetime.now().year),
            "model": None
        }
        # Detect templateset
        templateset = "application"
        if options["model"]:
            templateset = "modelapplication"
            vars["model"] = options["model"]
        if options["report"]:
            templateset = {
                "simple": "simplereport"
            }[options["report"]]
        # Check templateset
        ts_root = os.path.join("main", "templates", "newapp", templateset)
        if not os.path.isdir(ts_root):
            raise CommandError("Inconsistent template set %s" % templateset)
        # Get installed modules
        modules = set([a[4:] for a in INSTALLED_APPS if a.startswith("noc.")])
        # Fill templates
        for app in args:
            print "Creating skeleton for %s" % app
            m, a = app.split(".", 1)
            if "." in a:
                raise CommandError("Application name must be in form <module>.<app>")
            if m not in modules:
                raise CommandError("Invalid module: %s" % m)
            # Fill template variables
            tv = vars.copy()
            tv["module"] = m
            tv["app"] = a
            # Check applications is not exists
            app_root = os.path.join(m, "apps", a)
            if os.path.exists(app_root):
                raise CommandError("Application %s is already exists" % app)
            # Create apps/__init__.py if missed
            apps_root = os.path.join(m, "apps")
            if not os.path.exists(apps_root):
                self.create_dir(apps_root)
            apps_init = os.path.join(apps_root, "__init__.py")
            if not os.path.exists(apps_init):
                self.create_file(apps_init, "")
            # Create application directory
            self.create_dir(app_root)
            # Fill templates
            for dirpath, dirnames, files in os.walk(ts_root):
                dp = dirpath.split(os.sep)[4:]  # strip main/templates/newapp/<ts>/
                # Create directories
                for d in dirnames:
                    p = [app_root] + dp + [d]
                    self.create_dir(os.path.join(*p))
                for fn in files:
                    if fn == "DELETE":
                        continue
                    # Fill template
                    with open(os.path.join(dirpath, fn)) as f:
                        template = f.read()
                    for k, v in tv.items():
                        template = template.replace("{{%s}}" % k, v if v else "")
                    # Write template
                    p = [app_root] + dp + [fn]
                    self.create_file(os.path.join(*p), template)
