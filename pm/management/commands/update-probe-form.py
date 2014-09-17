# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Update Probe Form
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import logging
import datetime
from optparse import make_option
## Django modules
from django.core.management.base import BaseCommand, CommandError
from django.template import Template, Context
## NOC modules
from noc.pm.probes.base import probe_registry

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Manage Jobs
    """
    help = "Update Probe Form"
    option_list=BaseCommand.option_list + (
        make_option(
            "--force", "-f",
            action="store_true",
            dest="force",
            default=False,
            help="Force update (write over existing file)"
        ),
    )

    def handle(self, *args, **options):
        self.force = options["force"]
        if not len(args):
            raise CommandError("No probe module set")
        for path in args:
            if not path.endswith(".py"):
                raise CommandError("Invalid path %s" % path)
            self.update_form(path)

    def update_form(self, path):
        pc = None
        pcls = None
        m = "noc.%s." % path[:-3].replace(os.path.sep, ".")
        for c in probe_registry.probe_classes:
            if c.startswith(m):
                pc = probe_registry.probe_classes[c]
                pcls = c
                break
        if not pc:
            raise CommandError("Cannot load class %s" % path)
        if hasattr(pc, "_CONFIG_FORM"):
            pc.CONFIG_FORM = pc._CONFIG_FORM
        if not hasattr(pc, "CONFIG_FORM") or not pc.CONFIG_FORM:
            raise CommandError("No CONFIG_FORM attribute")
        # Determine JS path
        if pc.CONFIG_FORM.endswith(".js"):
            pc.CONFIG_FORM = m.CONFIG_FORM[:-3]
        if "." not in pc.CONFIG_FORM:
            parts = pc.__module__.split(".")
            if parts[0] == "noc":
                parts = parts[1:-1]
            else:
                parts = parts[:-1]
            extcls = "NOC.metricconfig.%s.%s" % (
                ".".join(parts), pc.CONFIG_FORM
            )
        else:
            extcls = pc.CONFIG_FORM
        parts = extcls.split(".")[2:]
        js_parts = parts[:-1] + [parts[-1] + ".js"]
        js_path = os.path.join(*js_parts)
        # Check file is already exists
        if os.path.isfile(js_path):
            if self.force:
                logging.info("File %s is already exists. Overwriting",
                             js_path)
            else:
                raise CommandError("File %s is already exists" % js_path)
        # Get probe vars
        pvars = []  # {name: ..., required: }
        rv = set()
        ov = set()
        for mt in probe_registry.class_probes[pcls]:
            for hi in probe_registry.class_probes[pcls][mt]:
                rv |= hi.req
                ov |= hi.opt
        ov -= rv
        pvars += [
            {
                "name": n,
                "xtype": "textfield",
                "fieldLabel": n,
                "allowBlank": False
            } for n in sorted(rv)]
        pvars += [
            {
                "name": n,
                "xtype": "textfield",
                "fieldLabel": n,
                "allowBlank": True
            } for n in sorted(ov)]
        l = len(pvars) - 1
        for i, v in enumerate(pvars):
            v["sep"] = "," if i < l else ""
        # Expand template
        with open("main/templates/ProbeConfig.js") as f:
            t = Template(f.read())
        content = t.render(Context({
            "pvars": pvars,
            "year": datetime.date.today().year,
            "extcls": extcls
        }))
        # Write file
        logger.info("Writing file %s", js_path)
        with open(js_path, "w") as f:
            f.write(content)
