# ----------------------------------------------------------------------
# Documentation macroses
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
from collections import defaultdict
import json
import glob
import logging
from typing import List, Dict
import yaml
from pathlib import Path


ROOT = os.getcwd()
PROFILES_ROOT = os.path.join(ROOT, "sa", "profiles")
DOC_ROOT = os.path.join(ROOT, "docs")
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
                x.split(".", 1)[0]
                for x in os.listdir(os.path.join(DOC_ROOT, "scripts-reference"))
                if x.endswith(".md") and not x.startswith(".") and not x.startswith("index.")
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
            r += [f"[{script}](../../scripts-reference/{script}.md) | {mark}"]
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
                "    You may be first to [contribute](../../sharing-collections-howto/index.md)",
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
                f"| [{profile}](../profiles-reference/{vendor}/{profile.split('.', 1)[1]}.md) |"
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

    @env.macro
    def vendor_profiles(vendor: str) -> str:
        r = []
        for fn in os.listdir(os.path.join("docs", "profiles-reference", vendor)):
            if not fn.endswith(".md") or "." in fn[:-3]:
                continue
            if fn.startswith("."):
                continue
            if fn.startswith("index."):
                continue
            if fn == "SUMMARY.md":
                continue
            r += [fn[:-3]]
        if not r:
            msg = f"Invalid vendor: {vendor}"
            raise ValueError(msg)
        return "\n".join(f"- [{vendor}.{x}]({x}.md)" for x in sorted(r)) + "\n"

    def check_exists(path: str):
        if os.path.exists(path):
            return
        cwd = os.getcwd()
        logger.error("[NOC] Path doesn't exists: %s", path)
        logger.error("[NOC] Current directory: %s", cwd)
        logger.error("[NOC] Current directory list: %s", ", ".join(os.listdir(cwd)))
        raise FileNotFoundError(path)

    @env.macro
    def show_highlights(items: List[Dict[str, str]]) -> str:
        r = [
            "<section class='noc-highlights-section'>",
            # "<div class='dark-mask'></div>",
            "<div class='noc-highlights'>",
        ]
        for item in items:
            r += [
                "<div class='item'>",
                f"<div class='title'>{item['title']}</div>",
                f"<div class='text'>{item['description']}</div>",
                f"<div class='link'><a href='highlights/{item['link']}/'>More...</a></div>",
                "</div>",
            ]
        r += ["</div>", "</section>"]
        return "\n".join(r)

    @env.macro
    def ui_path(*args: List[str]) -> str:
        """
        Renders neat UI path in form `ARG1 > ARG2 > ARG3`
        """
        return " > ".join(f"`{x}`" for x in args)

    @env.macro
    def ui_button(title: str) -> str:
        """
        Renders neat UI button.
        """
        return f"`{title}`"

    @env.macro
    def config_param(param: str) -> str:
        """
        Generate definition table for config params.
        """
        nonlocal config_params
        if not config_params:
            path = Path("docs", "config-reference", "params.yml")
            with open(path) as fp:
                defs = yaml.load(fp.read(), yaml.SafeLoader)
                config_params = defs["params"]
        p = config_params[param]
        r = [""]
        default = p.get("default")
        if default is not None:
            r.append(f"- **Default value:** `{default}`")
        choices = p.get("choices")
        if choices is not None:
            r.append("- **Possible values:**")
            r.append("")
            for x in choices:
                r.append(f"       - `{x}`")
            r.append("")
        # Paths
        r.append(f"- **YAML Path:** `{param}`")
        kv_path = param.replace(".", "/")
        r.append(f"- **Key-value Path:** `{kv_path}`")
        env_path = f"NOC_{param.replace('.','_').upper()}"
        r.append(f"- **Environment:** `{env_path}`")
        r.append("")
        return "\n".join(r)

    scripts = []  # Ordered list of scripts
    platforms = defaultdict(set)  # vendor -> {platform}
    script_profiles = defaultdict(set)  # script -> {profile}
    config_params = {}
