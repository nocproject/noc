#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## CustomerPortal Paste CLI tool
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
from optparse import OptionParser
import sys
## NOC modules
from noc.support.cp import CPClient


def die(msg=None, quiet=False):
    if not quiet:
        sys.stderr.write(msg + "\n")
    sys.exit(1)


def handle_upgrade(status, log, quiet=False):
    cp = CPClient()
    if not cp.has_system():
        die("System is not registred", quiet)
    if log:
        with open(log) as f:
            log = f.read()
    try:
        cp.upgrade(status, log)
    except CPClient.Error, why:
        die("RPC Error: %s" % why, quiet)


def parse_ttl(ttl):
    if ttl is None:
        return 86400 * 7
    scale = 1
    if ttl.endswith("h"):
        scale = 3600
        ttl = ttl[:-1]
    elif ttl.endswith("d"):
        scale = 86400
        ttl = ttl[:-1]
    elif ttl.endswith("w"):
        scale = 86400 * 7
        ttl = ttl[:-1]
    elif ttl.endswith("m"):
        scale = 86400 * 30
        ttl = ttl[:-1]
    elif ttl.endswith("y"):
        scale = 86400 * 365
        ttl = ttl[:-1]
    try:
        ttl = int(ttl)
    except ValueError:
        die("Invalid TTL", False)
    return ttl * scale


def main():
    parser = OptionParser()
    parser.add_option("--public", dest="public", action="store_true",
                      default=False, help="Create public paste"),
    parser.add_option("-s", "--subject", dest="subject", action="store",
                      help="Create paste subject")
    parser.add_option("-e", "--expire", dest="expire", action="store",
                      help="Set expiration time")
    parser.add_option("-q", "--quiet", dest="quiet", action="store_true")
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true")
    options, args = parser.parse_args()
    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)
    elif options.quiet:
        logging.basicConfig(level=logging.CRITICAL)
    else:
        logging.basicConfig()
    cp = CPClient()
    quiet = bool(options.quiet)
    if not cp.has_system():
        die("System is not registred", quiet)
    if args:
        data = []
        for a in args:
            with open(a) as f:
                data += [f.read()]
        data = "".join(data)
    else:
        data = sys.stdin.read()
    print cp.create_paste(
        subject=options.subject,
        data=data,
        syntax=None,
        ttl=parse_ttl(options.expire),
        public=bool(options.public)
    )["url"]

if __name__ == "__main__":
    logging.basicConfig(level=logging.CRITICAL)
    main()
