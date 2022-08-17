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
import glob


def define_env(env):
    YES = ":material-check:"
    NO = ":material-close:"

    def load_scripts() -> None:
        nonlocal scripts

        if scripts:
            return
        # Load list of all scripts
        scripts = list(
            sorted(
                x[:-3]
                for x in os.listdir(os.path.join(doc_root, "dev", "reference", "scripts"))
                if x.endswith(".md") and not x.startswith(".")
            )
        )

    @env.macro
    def mr(iid: int) -> str:
        """
        Link to Merge Request. Usage:

        {{ mr(123) }}
        :param iid:
        :return:
        """
        return f"[MR{iid}](https://code.getnoc.com/noc/noc/merge_requests/{iid})"

    @env.macro
    def supported_scripts(profile: str) -> str:
        nonlocal scripts
        r = ["Script | Support", "--- | ---"]
        load_scripts()
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
                mark = YES
            else:
                mark = NO
            r += [f"[{script}](../../../../dev/reference/scripts/{script}.md) | {mark}"]
        r += [""]
        return "\n".join(r)

    @env.macro
    def supported_platforms(vendor: str) -> str:
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

    @env.macro
    def supported_profiles(script: str) -> str:
        nonlocal script_profiles, scripts

        load_scripts()
        if not script_profiles:
            s_set = set(scripts)
            for m in glob.glob("sa/profiles/*/*/*.py"):
                parts = m.split("/")
                sn = parts[-1][:-3]
                if sn not in s_set:
                    continue
                script_profiles[sn].add(f"{parts[2]}.{parts[3]}")
        r = []
        s_profiles = [
            (profile.split(".")[0], profile) for profile in sorted(script_profiles[script])
        ]
        if s_profiles:
            r += [
                "| Profile |",
                "| --- |",
            ]
            r += [
                f"| [{profile}](../../../user/reference/profiles/{vendor}/{profile}.md) |"
                for vendor, profile in s_profiles
            ]
            r += [""]
        else:
            r += [
                "!!! todo",
                "    Script is not supported yet",
                "",
            ]
        return "\n".join(r)

    def get_detail(rules):
        """
        <details>

        | Key     | Value                                |
        |--------------------------------------|--------------------------------------|
        | message | XXXX                   xxxxxxxxxxxxx |
        |         | <Rule Name>                                  |
        | message | XXXX                   xxxxxxxxxxxxx |
        </details>

        :return:
        """
        r = ["<details>", "", "", "| Key     | Value  |", "| --- | --- |"]
        for item in rules:
            r += [f"|   | {item.data['name'].replace('|', '&#124')}  |"]
            for p in item.data["patterns"]:
                if p["key_re"] in {"^source$", "^profile$"}:
                    continue
                r += [f"| {p['key_re']} | {p['value_re']} |"]
        r += ["", "", "</details>"]
        return "\n".join(r)

    @env.macro
    def supported_events(profile: str) -> str:
        nonlocal profile_events

        from noc.core.collection.base import Collection

        rules_collections = Collection("fm.eventclassificationrules")

        if not profile_events:
            for item in rules_collections.get_items().values():
                if not item.data.get("patterns"):
                    continue
                p = [p["value_re"] for p in item.data["patterns"] if p["key_re"] == "^profile$"]
                if p:
                    p = p[0].strip("^$ ").replace("\\", "")
                else:
                    p = "Common"
                if p not in profile_events:
                    profile_events[p] = defaultdict(list)
                profile_events[p][item.data["event_class__name"]] += [item]
        r = []
        for cc in profile_events[profile]:
            c = [f"|{cc.replace('|', '&#124')} | x |", "| --- | --- |"]
            c += [get_detail(profile_events[profile][cc]), ""]
            r += c

        return "\n".join(r)

    scripts = []  # Ordered list of scripts
    platforms = defaultdict(set)  # vendor -> {platform}
    profile_events = {}  # profile -> [event_rules]
    script_profiles = defaultdict(set)  # script -> {profile}
    doc_root = "docs/ru/docs"
