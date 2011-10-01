# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Abstract module loader/registry
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import logging
import sys


class Registry(object):
    """
    Abstract module loader/registry
    """
    name = "Registry"  # Registry name
    subdir = "directory"  # Restrict to directory
    classname = "Class"  # Auto-register class
    apps = None  # Restrict to a list of application
    exclude = []  # List of excluded modules
    exclude_daemons = []  # List of excluded daemons

    def __init__(self):
        self.classes = {}
        # Detect daemon name
        _, self.daemon_name = os.path.split(sys.argv[0])
        if self.daemon_name.endswith(".py"):
            self.daemon_name = self.daemon_name[:-3]
        if self.daemon_name == "manage":
            self.daemon_name = sys.argv[1]
        #
        self.is_registered = self.daemon_name in self.exclude_daemons


    def register(self, name, module):
        """
        Should be called within metaclass' __new__ method
        """
        if name is None:
            return
        self.classes[name] = module

    def register_all(self):
        """
        Usually called at the top of the models.py
        """
        if self.is_registered:
            return
        logging.info("Loading %s" % self.name)
        if self.apps is None:
            from django.conf import settings
            apps = [a for a in settings.INSTALLED_APPS if a.startswith("noc.")]
        else:
            apps = self.apps
        for l in ["", "local"]:  # Look in the local/ directory too
            for app in apps:
                pd = os.path.join(l, app[4:], self.subdir)
                if not os.path.isdir(pd):
                    continue
                for dirpath, dirnames, filenames in os.walk(pd):
                    parts = dirpath.split(os.sep)
                    if "tests" in parts:
                        continue
                    if l:
                        mb = "noc.local.%s." % app[4:] + ".".join(parts[2:])
                        # Create missed __init__.py for local/
                        c = dirpath.split(os.sep)
                        for i in range(1, len(c) + 1):
                            i_path = os.path.join(os.sep.join(c[:i]),
                                                  "__init__.py")
                            if not os.path.exists(i_path):
                                open(i_path, "w").close()  # Create file
                    else:
                        mb = app + "." + ".".join(dirpath.split(os.sep)[1:])
                    for f in [f for f in filenames if not f.startswith(".") and f.endswith(".py")]:
                        if f == "__init__.py":
                            f = ""
                        else:
                            f = f[:-3]
                            if f in self.exclude:
                                continue
                            f = "." + f
                        __import__(mb + f, {}, {}, self.classname)
        self.is_registered = True

    def __getitem__(self, name):
        return self.classes[name]

    @property
    def choices(self):
        """
        For model field's choices=
        """
        return [(x, x) for x in sorted(self.classes.keys())]
