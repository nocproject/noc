# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Create and initialize solution
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import shutil
import os
## Django modules
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create new solution"

    src = os.path.join("main", "templates", "solution")

    def handle(self, *args, **options):
        for sol in args:
            self.create_solution(sol)

    def create_solution(self, sol):
        vendor, name = sol.split(".", 1)
        sd = os.path.join("solutions", vendor, name)
        if os.path.exists(sd):
            raise CommandError("%s is already exists" % sd)
        vp = os.path.join("solutions", vendor)
        if not os.path.exists(vp):
            print "Creating %s" % vp
            os.mkdir(vp)
        vpi = os.path.join(vp, "__init__.py")
        if not os.path.exists(vpi):
            print "Creating %s" % vpi
            with open(vpi, "w"):
                pass
        print "Initializing %s" % sd
        shutil.copytree(self.src, sd)
        print "Solution is ready"
