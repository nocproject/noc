# ----------------------------------------------------------------------
# Path utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 Gufo Labs
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from pathlib import Path
from typing import Optional
import re

# NOC modules
from .text import cyr_to_lat

_rx_safe_path = re.compile(r"[^a-z0-9\-\+]+", re.IGNORECASE)


def _clean_component(s: str) -> str:
    """
    Clean path component.

    Args:
        s: Input string.

    Returns:
        Cleaned output.
    """
    r = cyr_to_lat(s)
    r = _rx_safe_path.sub(" ", r).strip()
    return r.replace(" ", "_")


def safe_path(*args: str, sep: Optional[str] = None, suffix: Optional[str] = None) -> Path:
    """
    Expand path components to safe relative path.

    Suitable for collections. Unreadable or dangerous symbols are replaced
    with safe ones.

    Examples:

    ``` python
    safe_path(name, suffix=".json")
    ```

    ``` python
    safe_path(name, sep="|", suffix=".json")
    ```

    ``` python
    safe_path(vendor, profile, suffix=".json")
    ```

    Args:
        args: Path components.
        sep: Separator, if set, every `args` element is split by `sep`.
        suffix: If set, append suffix to filename. Suffix doesn't include
            dot, by default, so i.e. `.json` form must be used, rather than
            `json`.

    Returns:
        Formatted path component
    """
    if sep:
        components = []
        for arg in args:
            components.extend(arg.split(sep))
    else:
        components = list(args)
    components = [_clean_component(x) for x in components]
    path = Path(*(x for x in components if x))
    if suffix:
        path = path.with_suffix(suffix)
    return path


def safe_json_path(*args: str, sep: Optional[str] = "|", suffix: Optional[str] = ".json") -> Path:
    """
    Expand path components to JSON file path.

    Args:
        args: Path components.
        sep: Separator, if set, every `args` element is split by `sep`.
        suffix: If set, append suffix to filename. Suffix doesn't include
            dot, by default, so i.e. `.json` form must be used, rather than
            `json`.

    Returns:
        Formatted path component
    """
    return safe_path(*args, sep=sep, suffix=suffix)
