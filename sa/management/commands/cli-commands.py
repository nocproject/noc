# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Run version inventory
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import sys
import datetime
import time
from optparse import OptionParser, make_option
## Django modules
from django.core.management.base import BaseCommand, CommandError
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.reducetask import ReduceTask
from noc.sa.models.maptask import MapTask


class Command(BaseCommand):
    help = "Run cli commands from stdin or from file"
    option_list = BaseCommand.option_list + (
        make_option(
            "-L", "--limit", dest="limit",
            action="store", type="int",
            help="Limit concurrency"),
        make_option(
            "-t", "--timeout", dest="timeout",
            action="store", type="int",
            help="Script timeout"),
        make_option(
            "-c", "--command", dest="command", action="store",
            help="Commands to run, separated by \\n"
        ),
        make_option(
            "-i", "--input", dest="input", action="store",
            help="Input file containing commands, each per one line"
        ),
        make_option(
            "-T", "--target", dest="target", action="store",
            help="Input file containing managed objects or selectors, each per one line"
        ),
        make_option(
            "-d", "--debug", dest="debug", action="store_true",
            help="Debugging info"
        )
    )

    def handle(self, *args, **options):
        self.debug = bool(options.get("debug", True))
        # Build list of comands either from input file or from argument
        commands = []
        if options.get("command"):
            # Argument
            commands += options["command"].split("\\n")
        if options.get("input"):
            # Input file
            if not os.path.exists(options["input"]):
                raise CommandError("Input file '%s' is not found" % options["input"])
            with open(options["input"]) as f:
                commands += f.read().split("\n")
        if not commands:
            raise CommandError("No commands to perform")
        # Build list of targets
        targets = []
        if args:
            targets += list(args)
        if options.get("target"):
            # Input file
            if not os.path.exists(options["target"]):
                raise CommandError("Target file '%s' is not found" % options["target"])
            with open(options["target"]) as f:
                targets += f.read().split("\n")
        targets = [x.strip() for x in targets if x.strip()]
        if not targets:
            raise CommandError("No managed objects found")
        objects = []
        try:
            for x in targets:
                objects += ManagedObjectSelector.resolve_expression(x)
        except ManagedObject.DoesNotExist:
            raise CommandError("Managed object not found: '%s'" % x)
        except ManagedObjectSelector:
            raise CommandError("Managed object selector not found: '%s'" % x)
        # Run commands
        tasks = set()
        limit = options.get("limit", sys.maxint)
        timeout = options.get("timeout")
        while objects or tasks:
            # Spool next party
            while len(tasks) < limit and objects:
                o = objects.pop(0)
                mt = MapTask(
                    managed_object=o,
                    map_script="%s.commands" % o.profile_name,
                    script_params={"commands": commands},
                    next_try=datetime.datetime.now(),
                    script_timeout=timeout
                )
                mt.save()
                tasks.add(mt.id)
            # Check complete tasks
            complete = False
            for ct in MapTask.objects.filter(id__in=tasks, status__in=["C", "F"]):
                self.report_result(ct)
                tasks.remove(ct.id)
                ct.delete()
                complete = True
            if not complete:
                time.sleep(1)

    def report_result(self, task):
        mo = task.managed_object
        result = task.script_result
        if task.status == "C":
            print "@@@ %s: OK" % mo.name
            if self.debug:
                for c, r in zip(task.script_params["commands"], result):
                    print "> %s" % c
                    print r
        else:
            r = []
            if "code" in result:
                r += ["Error #%d" % result["code"]]
            if "text" in result:
                r += [result["text"]]
            er = ": ".join(r)
            print "@@@ %s: FAILED (%s)" % (mo.name, er)
