# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Script loader
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import sys
import glob
import logging
import inspect
import threading

import os
import re


## NOC modules
from base import BaseScript

logger = logging.getLogger(__name__)


class ScriptLoader(object):
    rx_requires = re.compile(
        "^\s+requires\s*=\s*\[([^\]]*)\]", re.DOTALL | re.MULTILINE
    )

    def __init__(self):
        self.scripts = {}  # Load scripts
        self.lock = threading.Lock()
        self.all_scripts = set()

    def get_script(self, name):
        """
        Load script and return BaseScript instance.
        Returns None when no script found or loading error occured
        """
        with self.lock:
            script = self.scripts.get(name)
            if not script:
                logger.info("Loading script %s", name)
                if not self.is_valid_name(name):
                    logger.error("Invalid script name")
                    return None
                vendor, system, sn = name.split(".")
                if os.path.exists(
                        os.path.join(
                            "sa", "profiles", vendor, system,
                            "%s.py" % sn
                        )
                ):
                    # Common script
                    module_name = "sa.profiles.%s" % name
                else:
                    # Generic script
                    module_name = "sa.profiles.Generic.%s" % sn
                try:
                    sm = __import__(module_name, {}, {}, "*")
                    for n in dir(sm):
                        o = getattr(sm, n)
                        if (
                            inspect.isclass(o) and
                            issubclass(o, BaseScript) and
                            o.__module__ == sm.__name__
                        ):
                            script = o
                            break
                    if not script:
                        logger.error("Script not found: %s", name)
                except Exception, why:
                    logger.error("Failed to load script %s: %s", name, why)
                    script = None
                self.scripts[name] = script
            return script

    def reload(self):
        """
        Reset script cache and release all modules
        """
        with self.lock:
            logger.info("Reloading scripts")
            for s in self.scripts:
                logger.debug("Reload script %s", s.name)
                reload(sys.modules[s.__module__])
            self.scripts = {}
            self.all_scripts = set()

    def is_valid_name(self, name):
        return ".." not in name

    def find_scripts(self):
        """
        Scan all available scripts
        """
        # Load generic scripts
        generics = {}  # Name -> dependencies
        for path in glob.glob("sa/profiles/Generic/*.py"):
            if path.endswith("/__init__.py"):
                continue
            gn = path.rsplit(os.sep)[-1][:-3]
            with open(path) as f:
                data = f.read()
                # Scan for requires = [..]
                match = self.rx_requires.search(data)
                if match:
                    generics[gn] = [
                        s.strip()[1:-1]
                        for s in match.group(1).split(",")
                        if s.strip()
                    ]
        # Load common scripts
        ns = set()
        profiles = set()
        for path in glob.glob("sa/profiles/*/*/*.py"):
            vendor, system, name = path.split(os.sep)[-3:]
            name = name[:-3]
            if name != "__init__":
                ns.add("%s.%s.%s" % (vendor, system, name))
                profiles.add("%s.%s" % (vendor, system))
        # Apply generic scripts
        for p in profiles:
            for g in generics:
                fgn = "%s.%s" % (p, g)
                if fgn in ns:
                    # Generic overriden with common script
                    continue
                if any(1 for r in generics[g]
                       if "%s.%s" % (p, r) not in ns):
                    continue  # Unsatisfied dependency
                # Add generic script
                ns.add(fgn)
        #
        with self.lock:
            self.all_scripts = ns

    def iter_scripts(self):
        """
        Returns all available script names
        """
        if not self.all_scripts:
            self.find_scripts()
        for s in sorted(self.all_scripts):
            yield s

    def has_script(self, name):
        """
        Check script is exists
        """
        if not self.all_scripts:
            self.find_scripts()
        return name in self.all_scripts

# Create singleton object
loader = ScriptLoader()
