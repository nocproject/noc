# ----------------------------------------------------------------------
# Documentation macroses
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
from collections import defaultdict
import json
import glob
import logging

ROOT = os.getcwd()
PROFILES_ROOT = os.path.join(ROOT, "sa", "profiles")
DOC_ROOT = os.path.join(ROOT, "docs", "en", "docs")
COLLECTIONS_ROOT = os.path.join(ROOT, "collections")
GITLAB_ROOT = "https://code.getnoc.com/noc/noc"

logger = logging.getLogger("mkdocs")
logger.info("[NOC] - Initializing NOC macroses")
logger.info("[NOC] - Current directory: %s", ROOT)
logger.info("[NOC] - Profiles root: %s", PROFILES_ROOT)
logger.info("[NOC] - Docs root: %s", DOC_ROOT)
logger.info("[NOC] - Collections root: %s", COLLECTIONS_ROOT)


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
                for x in os.listdir(os.path.join(DOC_ROOT, "dev", "reference", "scripts"))
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
        return f"[MR{iid}]({GITLAB_ROOT}/merge_requests/{iid})"

    @env.macro
    def supported_scripts(profile: str) -> str:
        nonlocal scripts
        r = ["Script | Support", "--- | ---"]
        load_scripts()
        # Get profile scripts
        vendor, name = profile.split(".")
        path = os.path.join(PROFILES_ROOT, vendor, name)
        check_exists(path)
        supported = {f[:-3] for f in os.listdir(path) if f.endswith(".py")}
        # Render
        for script in scripts:
            mark = YES if script in supported else NO
            r += [f"[{script}](../../../../dev/reference/scripts/{script}.md) | {mark}"]
        r += [""]
        return "\n".join(r)

    @env.macro
    def supported_platforms(vendor: str) -> str:
        nonlocal platforms

        if not platforms:
            # Load platforms
            for root, _, files in os.walk(os.path.join(COLLECTIONS_ROOT, "inv.platforms")):
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

    def check_exists(path: str):
        if os.path.exists(path):
            return
        cwd = os.getcwd()
        logger.error("[NOC] Path doesn't exists: %s", path)
        logger.error("[NOC] Current directory: %s", cwd)
        logger.error("[NOC] Current directory list: %s", ", ".join(os.listdir(cwd)))
        raise FileNotFoundError(path)

    scripts = []  # Ordered list of scripts
    platforms = defaultdict(set)  # vendor -> {platform}
    script_profiles = defaultdict(set)  # script -> {profile}
