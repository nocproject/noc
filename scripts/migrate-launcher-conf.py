#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Migrate noc-launcher config to supervisord
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
from ConfigParser import RawConfigParser

LEGACY_DAEMONS = [
    "noc-scheduler",
    "noc-web",
    "noc-sae",
    "noc-activator",
    "noc-classifier",
    "noc-collector",
    "noc-correlator",
    "noc-notifier",
    "noc-pmwriter",
    "noc-probe",
    "noc-discovery",
    "noc-sync"
]

def migrate():
    if not os.path.exists("etc/noc-launcher.conf"):
        print "noc-launcher.conf is not found. Exiting"
        return
    print "Migrating noc-launcher config"
    config = RawConfigParser()
    config.read("etc/noc-launcher.conf")
    for s in config.sections():
        if s not in LEGACY_DAEMONS:
            continue
        print "    ... migrating %s.conf" % s
        enabled = False
        user = None
        # group = None
        numprocs = len([o for o in config.options(s) if o.startswith("config")])
        if config.has_option(s, "enabled"):
            enabled = config.getboolean(s, "enabled")
        if config.has_option(s, "user"):
            user = config.get(s, "user")
        # if config.has_option(s, "enabled"):
        #    group = config.get(s, "group")
        new_conf = RawConfigParser()
        section = s[4:]  # Strip noc
        new_conf.add_section(section)
        new_conf.set(section, "autostart", "true" if enabled else "false")
        if user:
            new_conf.set(section, "user", user)
        if numprocs > 1:
            new_conf.set(section, "numprocs", numprocs)
        with open(os.path.join("etc", "config", "services",
                               "%s.conf" % section), "w") as f:
            new_conf.write(f)
    print "Removing etc/noc-launcher.conf"
    os.unlink("etc/noc-launcher.conf")

if __name__ == "__main__":
    migrate()
