#!/usr/bin/env python3
# ----------------------------------------------------------------------
# Dump requirements for given extras
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import sys
import re

REQUIREMENTS = "requirements.txt"

rx_extra = re.compile(r"extra\s*==\s*\"([^\"]+)\"")


def is_matched(req_extra, extras):
    if extras == "--all":
        return True
    return req_extra in extras


def main(extras):
    with open(REQUIREMENTS) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if not line.startswith("#") and ";" in line:
                req, env = line.split(";", 1)
                match = rx_extra.search(env)
                if match:
                    req_extra = match.group(1).strip()
                    if is_matched(req_extra, extras):
                        new_env = (env[: match.start()] + env[match.end() :]).strip()
                        if new_env:
                            print("%s;%s" % (req, new_env))
                        else:
                            print(req)
                    continue
            if not line.startswith("#"):
                print(line)


if __name__ == "__main__":
    main(sys.argv[1:])
