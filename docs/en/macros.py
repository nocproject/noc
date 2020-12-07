# ----------------------------------------------------------------------
# Documentation macroses
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
from collections import defaultdict
import json


def define_env(env):
    @env.macro
    def mr(iid: int):
        """
        Link to Merge Request. Usage:

        {{ mr(123) }}
        :param iid:
        :return:
        """
        return f"[MR{iid}](https://code.getnoc.com/noc/noc/merge_requests/{iid})"

    @env.macro
    def supported_scripts(profile: str):
        nonlocal scripts
        r = ["Script | Support", "--- | ---"]
        if not scripts:
            # Load list of all scripts
            scripts = list(
                sorted(
                    x[:-3]
                    for x in os.listdir(os.path.join(doc_root, "dev", "reference", "scripts"))
                    if x.endswith(".md") and not x.startswith(".")
                )
            )
        # Get profile scripts
        vendor, name = profile.split(".")
        supported = {
            f[:-3]
            for f in os.listdir(os.path.join("sa", "profiles", vendor, name))
            if f.endswith(".py")
        }
        # Render
        for script in scripts:
            if script in supported:
                mark = ":material-check:"
            else:
                mark = ":material-close:"
            r += [f"[{script}](../../../../dev/reference/scripts/{script}.md) | {mark}"]
        r += [""]
        return "\n".join(r)

    @env.macro
    def supported_platforms(vendor: str):
        nonlocal platforms

        if not platforms:
            # Load platforms
            for root, _, files in os.walk("collections/inv.platforms"):
                for fn in files:
                    if not fn.endswith(".json") or fn.startswith("."):
                        continue
                    with open(os.path.join(root, fn)) as f:
                        data = json.loads(f.read())
                    platforms[data["vendor__code"]].add(data["name"])
        v_platforms = list(sorted(platforms[vendor]))
        r = []
        if v_platforms:
            r += ["| Platform |", "| --- |"]
            r += [f"| {x} | " for x in v_platforms]
        else:
            r += [
                "!!! todo",
                "    Platform collection is not populated still.",
                "    You may be first to [contribute](../../../../dev/howto/sharing-collections/index.md)",
                "",
            ]
        return "\n".join(r)

    scripts = []  # Ordered list of scripts
    platforms = defaultdict(set)  # vendor -> {platform}
    doc_root = "docs/en/docs"
