# ----------------------------------------------------------------------
# Mkdocs macroses.
# Used with `mkdocs macros plugin`
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict
import os
from typing import DefaultDict, Set, Dict, Iterable, Any, List
from glob import glob

# Third-party modules
import orjson
from mkdocs_macros.plugin import MacrosPlugin


def define_env(env: MacrosPlugin):
    YES = ":material-check:"
    NO = ":material-close:"

    REPO_ROOT = os.path.join("..", "..")
    _platforms: DefaultDict[str, Set[str]] = defaultdict(set)  # vendor -> {platform,}
    _scripts: List[str] = []
    _generic_scripts: Set[str] = set()
    _profiles: Set[str] = set()

    def _iter_collection(collection: str) -> Iterable[Dict[str, Any]]:
        """
        Iterate and read all JSON within collection.

        Args:
            path: Collection root.

        Returns:
            Iterator yielding json data
        """
        path = os.path.join(REPO_ROOT, "collections", collection)
        for root, _, files in os.walk(path):
            for fn in files:
                if fn.startswith(".") or not fn.endswith(".json"):
                    continue
                with open(os.path.join(root, fn)) as f:
                    yield orjson.loads(f.read())

    def _get_platforms() -> Dict[str, Iterable[str]]:
        """
        Get list of supported platforms.

        Read collections and get a list of supported platforms.
        Caches result between calls.

        Returns:
            Dict of vendor -> iterable of platforms.
        """
        nonlocal _platforms

        if not _platforms:
            for data in _iter_collection("inv.platforms"):
                _platforms[data["vendor__code"]].add(data["name"])
        return _platforms

    def _get_profiles() -> Set[str]:
        nonlocal _profiles

        if not _profiles:
            _profiles = set(
                f"{p[-3]}.{p[-2]}"
                for p in (
                    fn.split(os.sep)
                    for fn in glob(
                        os.path.join(REPO_ROOT, "sa", "profiles", "*", "*", "profile.py")
                    )
                )
            )
        return _profiles

    def _get_scripts() -> List[str]:
        """
        Get list of supported scripts.

        Caches result between calls.

        Returns:
            Ordered list of supported scripts.
        """
        nonlocal _scripts

        if not _scripts:
            _scripts = list(
                sorted(
                    set(
                        fn.split(".")[0]
                        for fn in (
                            path.split(os.sep)[-1]
                            for path in glob(
                                os.path.join(REPO_ROOT, "docs", "scripts-reference", "docs", "*.md")
                            )
                        )
                        if not fn.startswith(".") and not fn.startswith("index.")
                    )
                )
            )
        return _scripts

    def _get_generic_scripts() -> Set[str]:
        """
        Get list of Generic scripts.

        Returns:
            Set of Generic script names.
        """
        nonlocal _generic_scripts
        if not _generic_scripts:
            _generic_scripts = set(
                fn[:-3]
                for fn in (
                    path.split(os.sep)[-1]
                    for path in glob(os.path.join(REPO_ROOT, "sa", "profiles", "Generic", "*.py"))
                )
                if not fn.startswith(".") and fn not in ("__init__.py", "profile.py")
            )
        return _generic_scripts

    def _get_profile_scripts(profile: str) -> Set[str]:
        vendor, name = profile.split(".")
        return set(
            fn[:-3]
            for fn in (
                path.split(os.sep)[-1]
                for path in glob(os.path.join(REPO_ROOT, "sa", "profiles", vendor, name, "*.py"))
            )
            if not fn.startswith(".") and fn not in ("__init__.py", "profile.py")
        )

    @env.macro
    def supported_platforms(vendor: str) -> str:
        """
        Render table of supported platforms for vendor.

        Used in:
            * Profiles Reference

        Args:
            vendor: Vendor name

        Returns:
            Redered table.
        """
        vendor_platforms = list(sorted(_get_platforms().get(vendor, set())))
        if not vendor_platforms:
            return "\n".join(
                [
                    "!!! todo",
                    "    Platform collection is not populated still.",
                    "    You may be first to [contribute](../../../../dev/howto/sharing-collections/index.md)",
                ]
            )
        r = ["| Platform |", "| --- |"]
        r += [f"| {platform} |" for platform in vendor_platforms]

        return "\n".join(r)

    @env.macro
    def supported_scripts(profile: str) -> str:
        impl_scripts = _get_profile_scripts(profile)
        generic_scripts = _get_generic_scripts()
        r = ["| Script | Support", "| --- | --- |"]
        for script in sorted(_get_scripts()):
            if script in impl_scripts:
                label = YES
            elif script in generic_scripts:
                label = f"{YES} (Generic)"
            else:
                label = NO
            r.append(f"| {script} | {label} |")
        r.append("")
        return "\n".join(r)

    def _profile_table(labels: Dict[str, str], default: str = "") -> str:
        """
        Render profile support table with given labels.

        Args:
            labels: Profile name to label match.
            default: Default label

        Returns:
            Rendered profile table.
        """
        vendors: DefaultDict[str, Set[str]] = defaultdict(set)
        for pn in _get_profiles():
            vendors[pn.split(".")[0]].add(pn)
        r = ["| Vendor | Profiles |", "| --- | --- |"]
        for vendor in sorted(vendors):
            for n, profile in enumerate(sorted(vendors[vendor])):
                label = labels.get(profile, default)
                r.append(f"| {vendor if n == 0 else ''} | {profile}: {label} |")
        r.append("")
        return "\n".join(r)

    @env.macro
    def script_profiles(name: str) -> str:
        """
        Render table of supported profiles for script.

        Used in:

            * Scripts Reference

        Args:
            name: Script name
        """
        impl_profiles = set(
            f"{p[-3]}.{p[-2]}"
            for p in (
                fn.split(os.sep)
                for fn in glob(os.path.join(REPO_ROOT, "sa", "profiles", "*", "*", f"{name}.py"))
            )
        )
        if name in _get_generic_scripts():
            default = f"{YES} (Generic)"
        else:
            default = NO
        return _profile_table({p: YES for p in impl_profiles}, default)

    @env.macro
    def mr(iid: int) -> str:
        """
        Link to Merge Request.

        Usage:

            {{ mr(123) }}

        Args:
            iid: MR id
        """
        return f"[MR{iid}](https://code.getnoc.com/noc/noc/merge_requests/{iid})"
