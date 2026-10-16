# ----------------------------------------------------------------------
# Documentation macroses
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict
import json
import logging
import yaml
from pathlib import Path


ROOT = Path.cwd()
SRC = ROOT / "src" / "noc"
PROFILES_ROOT = SRC / "sa" / "profiles"
DOC_ROOT = ROOT / "docs"
COLLECTIONS_ROOT = ROOT / "collections"
GITLAB_ROOT = "https://code.getnoc.com/noc/noc"
GITHUB_ROOT = "https://github.com/gufolabs/noc"

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
        scripts = sorted(
            x.stem
            for x in (DOC_ROOT / "scripts-reference").iterdir()
            if x.is_file()
            and x.suffix == ".md"
            and not x.name.startswith(".")
            and x.name != "index.md"
        )

    @env.macro
    def mr(iid: int) -> str:
        """
        Link to Merge Request. Usage:

        {{ mr(123) }}
        :return:
        """
        return f"[MR{iid}]({GITLAB_ROOT}/merge_requests/{iid})"

    @env.macro
    def gh(iid: str | int) -> str:
        """
        Create a link to a GitHub commit or pull request.

        The argument can be:
        - a short commit SHA (usually the first 6 characters);
        - a pull request number.

        Args:
            iid: GitHub commit short SHA or pull request number.

        Returns:
            Markdown link to the corresponding GitHub commit or pull request.

        Usage:

        Commit:
        ```text
        {{ gh("123456") }}
        ```

        Pull request:
        ```text
        {{ gh(123) }}
        ```
        """
        if isinstance(iid, int):
            return f"[#{iid}]({GITHUB_ROOT}/pull/{iid})"
        return f"[{iid}]({GITHUB_ROOT}/commit/{iid})"

    @env.macro
    def supported_scripts(profile: str) -> str:
        nonlocal scripts
        r = ["Script | Support", "--- | ---"]
        load_scripts()
        # Get profile scripts
        vendor, name = profile.split(".")
        path = PROFILES_ROOT / vendor / name
        check_exists(path)
        supported = {f.stem for f in path.iterdir() if f.is_file() and f.suffix == ".py"}
        # Render
        for script in scripts:
            mark = YES if script in supported else NO
            r.append(f"[{script}](../../scripts-reference/{script}.md) | {mark}")
        r.append("")
        return "\n".join(r)

    @env.macro
    def supported_platforms(vendor: str) -> str:
        nonlocal platforms

        if not platforms:
            # Load platforms
            for path in (COLLECTIONS_ROOT / "inv.platforms").rglob("*.json"):
                if path.name.startswith("."):
                    continue

                with path.open() as f:
                    data = json.load(f)

                platforms[data["vendor__code"]].add(data["name"])

        v_platforms = sorted(platforms[vendor])
        r: list[str] = []

        if v_platforms:
            r = [*r, "| Platform |", "| --- |", *(f"| {x} | " for x in v_platforms)]
        else:
            r = [
                *r,
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

            for path in PROFILES_ROOT.glob("*/*/*.py"):
                sn = path.stem
                if sn not in s_set:
                    continue

                vendor = path.parent.parent.name
                profile = path.parent.name
                script_profiles[sn].add(f"{vendor}.{profile}")

        s_profiles = [
            (profile.split(".", 1)[0], profile) for profile in sorted(script_profiles[script])
        ]
        r = []
        if s_profiles:
            r = [
                *r,
                "| Profile |",
                "| --- |",
                *(
                    f"| [{profile}](../profiles-reference/{vendor}/{profile.split('.', 1)[1]}.md) |"
                    for vendor, profile in s_profiles
                ),
                "",
            ]
        else:
            r = [
                *r,
                "!!! todo",
                "    Script is not supported yet",
                "",
            ]

        return "\n".join(r)

    @env.macro
    def vendor_profiles(vendor: str) -> str:
        r = []

        path = DOC_ROOT / "profiles-reference" / vendor
        r = [
            fn.stem
            for fn in path.iterdir()
            if (
                fn.is_file()
                and fn.suffix == ".md"
                and "." not in fn.stem
                and not fn.name.startswith(".")
                and not fn.name.startswith("index.")
                and fn.name != "SUMMARY.md"
            )
        ]
        if not r:
            msg = f"Invalid vendor: {vendor}"
            raise ValueError(msg)
        return "\n".join(f"- [{vendor}.{x}]({x}.md)" for x in sorted(r)) + "\n"

    def check_exists(path: Path) -> None:
        if path.exists():
            return
        cwd = Path.cwd()
        logger.error("[NOC] Path doesn't exists: %s", path)
        logger.error("[NOC] Current directory: %s", cwd)
        logger.error(
            "[NOC] Current directory list: %s",
            ", ".join(x.name for x in cwd.iterdir()),
        )
        raise FileNotFoundError(path)

    @env.macro
    def show_highlights(items: list[dict[str, str]]) -> str:
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
    def ui_path(*args: list[str]) -> str:
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
        env_path = f"NOC_{param.replace('.', '_').upper()}"
        r.append(f"- **Environment:** `{env_path}`")
        r.append("")
        return "\n".join(r)

    scripts = []  # Ordered list of scripts
    platforms = defaultdict(set)  # vendor -> {platform}
    script_profiles = defaultdict(set)  # script -> {profile}
    config_params = {}
