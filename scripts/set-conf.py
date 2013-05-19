#!/usr/bin/env python
##----------------------------------------------------------------------
## Change configuration file
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##---------------------------------------------------------------------

## Python modules
import sys
import ConfigParser


def usage():
    print "USAGE:"
    print "%s <config path> <section> <option> [<value>]" % sys.argv[0]
    sys.exit(1)


def set_conf(config, section, option, value=""):
    c = ConfigParser.SafeConfigParser()
    c.read(config)
    if section == "main":
        if option in ("logfile", "pidfile") and value:
            if not value.endswith("/"):
                value += "/"
            try:
                v = c.get(section, option)
            except ConfigParser.NoOptionError:
                return
            if not v:
                return
            if option == "logfile":
                value = v.replace("/var/log/noc/", value)
            elif option == "pidfile":
                value = v.replace("/var/run/noc/", value)
    c.set(section, option, value)
    with open(config, "w") as f:
        c.write(f)

if __name__ == "__main__":
    l = len(sys.argv)
    if l < 4 or l > 5:
        usage()
    set_conf(config=sys.argv[1], section=sys.argv[2],
             option=sys.argv[3],
             value=sys.argv[4] if len(sys.argv) == 5 else "")
