#!/usr/bin/env python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Install canned session to proper location
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import csv
import os
import re

rx_script = re.compile(r"^\s+script\s*=\s*\"(?P<script>.+?)\"", re.MULTILINE)
rx_q = re.compile(r"[^0-9a-zA-Z_]+")
rx_platform = re.compile(r"platform\s*=\s*['\"]([^']+)['\"]")
rx_version = re.compile(r"version\s*=\s*['\"]([^']+)['\"]")


def install_can(path, platform, version):
    with open(path) as f:
        data = f.read()
    # Try to get platform and version if not defined
    if platform is None:
        platform = rx_platform.search(data).group(1)
    if version is None:
        version = rx_version.search(data).group(1)
    # Get script name
    match = rx_script.search(data)
    script = match.group("script")
    v, o, s = script.split(".")
    p = os.path.join("sa", "profiles", v, o, "tests")
    if not os.path.exists(p):
        print "Creating directory %s" % p
        os.mkdir(p)
    init = os.path.join(p, "__init__.py")
    if not os.path.exists(init):
        print "Creating %s" % init
        with open(init, "w"):
            pass
    data = re.sub(r"platform\s*=\s*['\"]<<<INSERT YOUR PLATFORM HERE>>>['\"]",
                  "platform = \"%s\"" % platform,
                  data)
    data = re.sub(r"version\s*=\s*['\"]<<<INSERT YOUR VERSION HERE>>>['\"]",
                  "version = \"%s\"" % version,
                  data)
    mask = os.path.join(p,"%s_%s_%s_%s_%%04d.py" % (v, rx_q.sub("_", platform),
                                                    rx_q.sub("_", version), s))
    i = 1
    while True:
        oo = mask % i
        if not os.path.exists(oo):
            break
        i += 1
    print "Saving canned output into %s" % oo
    with open(oo, "w") as f:
        f.write(data)

def usage():
    print "USAGE:"
    print "%s -p <platform> -v <version> [-r ] path1 .. pathN" % sys.argv[0]
    sys.exit(0)

if __name__=="__main__":
    import sys
    import getopt
    platform = None
    version = None
    to_remove = False
    optlist, optarg = getopt.getopt(sys.argv[1:], "p:v:r")
    for k, v in optlist:
        if k == "-p":
            platform = v
        elif k == "-v":
            version = v
        elif k == "-r":
            to_remove = True
    #if platform is None or version is None:
    #    usage()
    for p in optarg:
        install_can(p, platform, version)
        if to_remove:
            print "Removing %s" % p
            os.unlink(p)
