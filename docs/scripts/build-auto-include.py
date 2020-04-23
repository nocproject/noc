# ----------------------------------------------------------------------
# Populate include/auto
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import glob
import os
import sys
from collections import defaultdict
import json

all_profiles = set()


def render_platform(vendor, data):
    global all_profiles

    profiles = [t for t in (data.get("tags") or []) if t in all_profiles]

    title = "%s %s" % (vendor, data["name"])
    r = [
        ".. _platforms-%s-%s:" % (vendor, data["name"]),
        "",
        "=" * len(title),
        title,
        "=" * len(title),
        "",
        ".. contents:: On this page",
        "    :local:",
        "    :backlinks: none",
        "    :depth: 2",
        "    :class: singlecol",
        "",
        ".. list-table::",
        "",
        "    * - Vendor",
        "      - %s" % vendor,
        "    * - Model",
        "      - %s" % data["name"],
    ]
    aliases = data.get("aliases")
    if aliases:
        r += ["    * - Aliases", "      - %s" % ", ".join(sorted(aliases))]
    r += [
        "    * - Start of Sale",
        "      - %s" % (data.get("start_of_sale") or "N/A"),
        "    * - End of Sale",
        "      - %s" % (data.get("end_of_sale") or "N/A"),
        "    * - End of Support",
        "      - %s" % (data.get("end_of_support") or "N/A"),
        "    * - End of Ext. Support",
        "      - %s" % (data.get("end_of_xsupport") or "N/A"),
    ]
    if len(profiles) == 1:
        r += ["    * - Profile", "      - :ref:`%s <profile-%s>`" % (profiles[0], profiles[0])]
    elif len(profiles) > 1:
        r += [
            "    * - Profiles",
            "      - %s" % ", ".join([":ref:`%s <profile-%s>`" % (p, p) for p in sorted(profiles)]),
        ]
    if data.get("snmp_sysobjectid"):
        r += ["    * - SNMP SysObjectId", "      - %s" % data["snmp_sysobjectid"]]
    r += [""]
    if data.get("description"):
        r += [data.get("description"), ""]
    return "\n".join(r)


def render_vendor_platforms(platforms):
    r = [".. hlist::", "    :columns: 3", ""]
    r += ["    * :ref:`%s <%s>`" % (name, ref) for name, ref in sorted(platforms)]
    r += [""]
    return "\n".join(r)


def render_vendor_index(vendor):
    r = [
        ".. _platforms-vendor-%s:" % vendor,
        "",
        "=" * len(vendor),
        vendor,
        "=" * len(vendor),
        "",
        ".. toctree::",
        "    :titlesonly:",
        "    :glob:",
        "",
        "    /platforms/%s-*" % vendor,
        "",
    ]
    return "\n".join(r)


def write_file(path, data):
    print("Writing %s" % path)
    with open(path, "w") as f:
        f.write(data)


def build_platforms(root, inc_root):
    global all_profiles

    coll_root = os.path.abspath(os.path.join(root, "collections", "inv.platforms"))
    if not os.path.exists(coll_root):
        return
    plat_root = os.path.abspath(os.path.join(root, "docs", "src", "en", "platforms"))
    if not os.path.exists(plat_root):
        os.makedirs(plat_root)
    vendor_platforms = defaultdict(list)
    profile_platforms = defaultdict(list)
    for path in glob.glob(os.path.join(coll_root, "*", "*.json")):
        vendor, jname = path.split(os.sep)[-2:]
        with open(path) as f:
            data = json.load(f)
        ref = "platforms-%s-%s" % (vendor, data["name"])
        plat_rst_path = os.path.join(plat_root, "%s-%s.rst" % (vendor, jname[:-5]))
        write_file(plat_rst_path, render_platform(vendor, data))
        tags = data.get("tags") or []
        vendor_platforms[vendor] += [(data["name"], ref)]
        for t in tags:
            if t in all_profiles:
                profile_platforms[t] += [(data["name"], ref)]
    # Vendor Platforms
    for vendor in vendor_platforms:
        # Vendor index
        write_file(os.path.join(plat_root, "vendor-%s.rst" % vendor), render_vendor_index(vendor))
        # Supported platform
        write_file(
            os.path.join(inc_root, "supported-vendor-platforms-%s.rst" % vendor),
            render_vendor_platforms(vendor_platforms[vendor]),
        )
    # Profile platforms
    for profile in profile_platforms:
        write_file(
            os.path.join(inc_root, "supported-profile-platforms-%s.rst" % profile),
            render_vendor_platforms(profile_platforms[profile]),
        )


def build_scripts(root, inc_root):
    global all_profiles

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
        r = ["* :ref:`%s <script-%s>`" % (s, s) for s in sorted(scripts[profile])]
        data = "\n".join(r)
        write_file(os.path.join(inc_root, "supported-scripts-%s.rst" % profile), data)
    # Build supported profiles
    for script in profiles:
        r = ["* :ref:`%s <profile-%s>`" % (p, p) for p in sorted(profiles[script])]
        data = "\n".join(r)
        write_file(os.path.join(inc_root, "supported-profiles-%s.rst" % script), data)
    all_profiles = set(scripts)


def main():
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    noc_root = os.path.abspath(os.path.join(my_path, "..", ".."))
    inc_root = os.path.abspath(os.path.join(noc_root, "docs", "src", "en", "include", "auto"))

    if not os.path.exists(inc_root):
        os.makedirs(inc_root)

    build_scripts(noc_root, inc_root)
    build_platforms(noc_root, inc_root)


if __name__ == "__main__":
    main()
