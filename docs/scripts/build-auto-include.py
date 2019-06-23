# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Populate include/auto
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
import glob
import os
import sys
from collections import defaultdict


def build_scripts(root, inc_root):
    scripts = defaultdict(list)
    profiles = defaultdict(list)
    for name in glob.glob(os.path.join(root, "sa", "profiles", "*", "*", "*.py")):
        parts = name.split(os.sep)[-3:]
        if parts[-1].startswith("_") or parts[-1] == "profile.py":
            continue
        profile = "%s.%s" % (parts[0], parts[1])
        script = os.path.splitext(parts[2])[0]
        scripts[profile] += [script]
        profiles[script] += [profile]
    # Build supported scripts
    for profile in scripts:
        with open(os.path.join(inc_root, "supported-scripts-%s.rst" % profile), "w") as f:
            r = [
                "* :ref:`%s <script-%s>`" % (s, s)
                for s in sorted(scripts[profile])
            ]
            data = "\n".join(r)
            f.write(data)
    # Build supported profiles
    for script in profiles:
        with open(os.path.join(inc_root, "supported-profiles-%s.rst" % script), "w") as f:
            r = [
                "* :ref:`%s <profile-%s>`" % (p, p)
                for p in sorted(profiles[script])
            ]
            data = "\n".join(r)
            f.write(data)


def main():
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    noc_root = os.path.abspath(os.path.join(my_path, "..", ".."))
    inc_root = os.path.abspath(os.path.join(noc_root, "docs", "src", "en", "include", "auto"))

    if not os.path.exists(inc_root):
        os.makedirs(inc_root)

    build_scripts(noc_root, inc_root)


if __name__ == "__main__":
    main()
